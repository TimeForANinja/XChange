from typing import Tuple, Any
import datetime
import gridfs
from flask import current_app
from apiflask import abort

def get_db():
    return current_app.db

def get_fs():
    return gridfs.GridFS(current_app.db)

def get_item_urls(item_id: str, item_type: str) -> dict:
    base_host = current_app.config['BASE_URL']
    if item_type == 'link':
        path = f"/r/{item_id}"
    else:
        path = f"/view/{item_id}"
    
    return {
        'base_host': base_host,
        'path': path,
        'uri': f"{base_host}{path}",
        'raw_uri': f"{base_host}/raw/{item_id}"
    }

def get_item_or_404(id: str, increment_access: bool = True) -> Tuple[dict, Any]:
    db = get_db()
    fs = get_fs()
    items = db.items
    
    item = items.find_one({'_id': id})
    if not item:
        abort(404, 'Item not found')

    # Check expiration
    now = datetime.datetime.now(datetime.UTC).replace(tzinfo=None)
    if item['expires_at'] and item['expires_at'] < now:
        items.delete_one({'_id': id})
        if item.get('file_id'):
            fs.delete(item['file_id'])
        abort(404, 'Item expired')

    # Check access limit
    if item['access_limit'] > 0 and item['access_count'] >= item['access_limit']:
        items.delete_one({'_id': id})
        if item.get('file_id'):
            fs.delete(item['file_id'])
        abort(404, 'Access limit reached')

    # Fetch content
    content = None
    if item['type'] in ['file', 'image']:
        try:
            grid_out = fs.get(item['file_id'])
            content = grid_out.read()
            item['mimetype'] = grid_out.content_type
        except:
            content = None
    else:
        content = item.get('content')

    if increment_access:
        # already have 'now' as naive UTC
        items.update_one({'_id': id}, {
            '$inc': {'access_count': 1},
            '$set': {'last_access': now}
        })
        item['access_count'] += 1
        item['last_access'] = now

        # Check if we just reached the limit
        if item['access_limit'] > 0 and item['access_count'] >= item['access_limit']:
            # Delete from DB so it doesn't show in Admin UI
            items.delete_one({'_id': id})
            if item.get('file_id'):
                fs.delete(item['file_id'])

    return item, content
