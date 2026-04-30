import os
import datetime
import base64
from apiflask import APIBlueprint as Blueprint, abort
from flask import redirect, request, render_template, current_app, Response
from werkzeug.utils import secure_filename

from routes_schema import CreateItemSchema, ConfigSchema, ItemResponseSchema, ItemDetailSchema
from naming import generate_base64_id, generate_human_id
from routes.utils import get_item_or_404, get_db, get_fs, get_item_urls

api_bp = Blueprint('api', __name__)

@api_bp.get('/config')
@api_bp.output(ConfigSchema)
def get_config():
    """Get application feature flags and configuration."""
    return {
        'ENABLE_ADMIN_UI': current_app.config['ENABLE_ADMIN_UI'],
        'ENABLE_UNLIMITED_USAGE': current_app.config['ENABLE_UNLIMITED_USAGE'],
        'ENABLE_UNLIMITED_AGE': current_app.config['ENABLE_UNLIMITED_AGE'],
        'ENABLE_FAST_FORWARD': current_app.config['ENABLE_FAST_FORWARD'],
        'MAX_FILE_SIZE': current_app.config['MAX_FILE_SIZE'],
        'VERSION': current_app.version,
    }

@api_bp.post('/items')
@api_bp.input(CreateItemSchema, location='form_and_files', arg_name='data')
@api_bp.output(ItemResponseSchema, status_code=201)
def create_item(data: dict):
    """Create a new item (text, link, file, or image)."""
    db = get_db()
    items = db.items
    fs = get_fs()

    # Feature Flag: Allow Create From
    allowed_hosts = current_app.config.get('ALLOW_CREATE_FROM', [])
    if allowed_hosts:
        current_host = request.host
        current_domain = current_host.split(':')[0]
        if current_host not in allowed_hosts and current_domain not in allowed_hosts:
            abort(403, 'Creation is not allowed from this domain')

    # Feature Flags: Unlimited
    if not current_app.config['ENABLE_UNLIMITED_USAGE'] and data['access_limit'] == 0:
        abort(400, 'Unlimited access is disabled')
    if not current_app.config['ENABLE_UNLIMITED_AGE'] and data['time_limit'] == 'unlimited':
        abort(400, 'Unlimited time is disabled')

    # Feature Flag: Fast Forward
    fast_forward = data['fast_forward']
    if not current_app.config['ENABLE_FAST_FORWARD']:
        fast_forward = False

    item_id = generate_human_id() if data['name_type'] == 'human' else generate_base64_id()
    while items.find_one({'_id': item_id}):
        item_id = generate_human_id() if data['name_type'] == 'human' else generate_base64_id()

    expires_at = None
    if data['time_limit'] != 'unlimited':
        days = int(data['time_limit'].replace('d', ''))
        expires_at = (datetime.datetime.now(datetime.UTC) + datetime.timedelta(days=days)).replace(tzinfo=None)

    item = {
        '_id': item_id,
        'type': data['type'],
        'access_limit': data['access_limit'],
        'access_count': 0,
        'last_access': None,
        'expires_at': expires_at,
        'created_at': datetime.datetime.now(datetime.UTC).replace(tzinfo=None),
        'fast_forward': fast_forward,
        'syntax': data.get('syntax', 'plain')
    }

    if data['type'] in ['text', 'link']:
        item['content'] = data.get('content')
    elif data['type'] in ['file', 'image']:
        file = data.get('file')
        if not file:
            abort(400, 'No file provided')

        file.seek(0, os.SEEK_END)
        size = file.tell()
        if size > current_app.config['MAX_FILE_SIZE']:
            abort(413, f"File too large. Max size: {current_app.config['MAX_FILE_SIZE']} bytes")
        file.seek(0)

        if file.content_type and file.content_type.startswith('image/'):
            item['type'] = 'image'

        filename = secure_filename(file.filename)
        file_id = fs.put(file, filename=filename, content_type=file.content_type)
        item['file_id'] = file_id
        item['filename'] = filename

    items.insert_one(item)

    urls = get_item_urls(item_id, data['type'])
    return {
        'id': item_id,
        **urls
    }

@api_bp.get('/api/items/<id>')
@api_bp.output(ItemDetailSchema)
def get_item_api(id: str):
    """Get item metadata and content for in-memory viewing."""
    item, content = get_item_or_404(id)
    urls = get_item_urls(id, item['type'])

    res = {
        'id': id,
        'type': item['type'],
        'access_limit': item['access_limit'],
        'access_count': item['access_count'],
        'last_access': item['last_access'].isoformat() if item['last_access'] else None,
        'created_at': item['created_at'].isoformat() if item['created_at'] else None,
        **urls
    }
    if item.get('expires_at'):
        res['expires_at'] = item['expires_at'].isoformat()

    if item['type'] in ['text', 'link']:
        res['content'] = content
        if item['type'] == 'text':
            res['syntax'] = item.get('syntax', 'plain')
    else:
        res['filename'] = item.get('filename')
        res['mimetype'] = item.get('mimetype')
        if content:
            res['content'] = base64.b64encode(content).decode('utf-8')
        else:
            res['content'] = None

    return res


@api_bp.get('/raw/<id>')
@api_bp.doc(summary="Get raw item content", description="Returns raw content suitable for curl.")
def get_raw_item(id: str):
    """Retrieve the raw content of an item for CLI tools (no redirects, no attachment header)."""
    item, content = get_item_or_404(id)

    if item['type'] == 'link':
        return item['content'], 200, {'Content-Type': 'text/plain; charset=utf-8'}

    if item['type'] == 'text':
        return content, 200, {'Content-Type': 'text/plain; charset=utf-8'}

    if item['type'] in ['file', 'image']:
        if not content:
            return abort(404, "File not found in storage")

        return Response(
            content,
            mimetype=item.get('mimetype')
        )

@api_bp.get('/r/<id>')
@api_bp.doc(summary="Short redirect or direct access", description="Returns raw text, redirects for links, or downloads for files.")
def short_redirect(id: str):
    """Retrieve the content of an item (Short URL)."""
    item, content = get_item_or_404(id)

    if item['type'] == 'link':
        if item['fast_forward'] and current_app.config['ENABLE_FAST_FORWARD']:
            return redirect(item['content'])
        else:
            return render_template('redirect.html', url=item['content'])

    return abort(404, "Item is not a link")
