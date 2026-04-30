import datetime
from apiflask import APIBlueprint as Blueprint, abort
from flask import request, current_app

from routes_schema import AdminItemSchema, MessageSchema, UpdateItemSchema
from routes.utils import get_db, get_fs, get_item_urls

admin_bp = Blueprint('admin', __name__)

@admin_bp.get('/admin/items')
@admin_bp.output(AdminItemSchema(many=True))
def admin_list_items():
    """List all items for admin."""
    if not current_app.config['ENABLE_ADMIN_UI']:
        abort(404)
    
    token = request.headers.get('Authorization')
    if token != f"Bearer {current_app.config['ADMIN_TOKEN']}":
        abort(401, 'Unauthorized')

    db = get_db()
    
    type_filter = request.args.get('type')
    search_filter = request.args.get('search')
    
    query = {}
    if type_filter:
        query['type'] = type_filter
    if search_filter:
        query['_id'] = {'$regex': search_filter, '$options': 'i'}

    items_list = list(db.items.find(query))

    for item in items_list:
        item['id'] = item['_id']
        urls = get_item_urls(item['id'], item['type'])
        item.update(urls)

    return items_list

@admin_bp.delete('/admin/items/<id>')
@admin_bp.output(MessageSchema)
def admin_delete_item(id: str):
    """Force delete an item."""
    if not current_app.config['ENABLE_ADMIN_UI']:
        abort(404)
        
    token = request.headers.get('Authorization')
    if token != f"Bearer {current_app.config['ADMIN_TOKEN']}":
        abort(401, 'Unauthorized')

    db = get_db()
    fs = get_fs()
    item = db.items.find_one({'_id': id})
    if not item:
        abort(404, 'Item not found')

    db.items.delete_one({'_id': id})
    if item.get('file_id'):
        fs.delete(item['file_id'])

    return {'message': 'Item deleted successfully'}

@admin_bp.patch('/admin/items/<id>')
@admin_bp.input(UpdateItemSchema, arg_name='data')
@admin_bp.output(AdminItemSchema)
def admin_update_item(id: str, data: dict):
    """Update item properties (ID, Limits)."""
    if not current_app.config['ENABLE_ADMIN_UI']:
        abort(404)

    token = request.headers.get('Authorization')
    if token != f"Bearer {current_app.config['ADMIN_TOKEN']}":
        abort(401, 'Unauthorized')

    db = get_db()
    items = db.items
    item = items.find_one({'_id': id})
    if not item:
        abort(404, 'Item not found')

    update_query = {}
    new_id = data.get('id')
    
    if 'access_limit' in data:
        update_query['access_limit'] = data['access_limit']
    
    if 'time_limit' in data:
        if data['time_limit'] == 'unlimited':
            update_query['expires_at'] = None
        else:
            days = int(data['time_limit'].replace('d', ''))
            update_query['expires_at'] = (datetime.datetime.now(datetime.UTC) + datetime.timedelta(days=days)).replace(tzinfo=None)

    if new_id and new_id != id:
        if items.find_one({'_id': new_id}):
            abort(400, 'New ID already exists')

        # Create new document with new ID
        new_item = item.copy()
        new_item['_id'] = new_id
        # Apply updates
        for k, v in update_query.items():
            new_item[k] = v

        items.insert_one(new_item)
        items.delete_one({'_id': id})
        item = new_item
    elif update_query:
        items.update_one({'_id': id}, {'$set': update_query})
        item = items.find_one({'_id': id})

    # Prepare response
    item['id'] = item['_id']
    urls = get_item_urls(item['id'], item['type'])
    item.update(urls)
    
    return item
