from apiflask import APIBlueprint as Blueprint, abort
from flask import send_from_directory, request, current_app

frontend_bp = Blueprint('frontend', __name__)

@frontend_bp.get('/assets/<path:path>')
def send_assets(path: str):
    """Serve static assets (JS, CSS)."""
    return send_from_directory('../frontend/assets', path)

def is_creation_allowed():
    """Check if creation is allowed from the current host."""
    allowed_hosts = current_app.config.get('ALLOW_CREATE_FROM', [])
    if not allowed_hosts:
        return True
    
    current_host = request.host
    current_domain = current_host.split(':')[0]
    return current_host in allowed_hosts or current_domain in allowed_hosts

@frontend_bp.get('/')
def index():
    """Serve main frontend page."""
    if not is_creation_allowed():
        return send_from_directory('../frontend', 'forbidden.html'), 403
    
    return send_from_directory('../frontend', 'create.html')

@frontend_bp.get('/view/<id>')
def view_page(id: str):
    """Serve viewing frontend page."""
    return send_from_directory('../frontend', 'view.html')

@frontend_bp.get('/admin')
def admin_page():
    """Serve admin frontend page."""
    if not current_app.config['ENABLE_ADMIN_UI']:
        abort(404)
    
    if not is_creation_allowed():
        return send_from_directory('../frontend', 'forbidden.html'), 403

    return send_from_directory('../frontend', 'admin.html')
