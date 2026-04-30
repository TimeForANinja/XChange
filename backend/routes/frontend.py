from apiflask import APIBlueprint as Blueprint, abort
from flask import send_from_directory, request, current_app

frontend_bp = Blueprint('frontend', __name__)

@frontend_bp.get('/assets/<path:path>')
def send_assets(path: str):
    """Serve static assets (JS, CSS)."""
    return send_from_directory('../frontend/assets', path)

@frontend_bp.get('/')
def index():
    """Serve main frontend page."""
    # Check if creation is allowed from this domain
    allowed_hosts = current_app.config.get('ALLOW_CREATE_FROM', [])
    if allowed_hosts:
        current_host = request.host
        current_domain = current_host.split(':')[0]
        # Strict FQDN check as requested
        if current_host not in allowed_hosts and current_domain not in allowed_hosts:
            return "Creation is not allowed from this domain. You can only view items.", 403
    
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
    return send_from_directory('../frontend', 'admin.html')
