from apiflask import APIFlask
from flask_cors import CORS
from pymongo import MongoClient
from flask_compress import Compress

from routes.frontend import frontend_bp
from routes.api import api_bp
from routes.admin import admin_bp

def create_app():
    app = APIFlask(__name__, title='XChange API', static_folder='../frontend', static_url_path='', version='1.0.0')
    CORS(app)

    # Default Configuration
    app.config.from_mapping(
        MONGO_HOST='localhost',
        MONGO_PORT=27017,
        MONGO_DBNAME='xchange',
        MONGO_USER=None,
        MONGO_PASSWORD=None,
        ADMIN_TOKEN='admin-secret',
        BASE_URL='http://localhost:5000',
        ENABLE_ADMIN_UI=False,
        ENABLE_UNLIMITED_USAGE=True,
        ENABLE_UNLIMITED_AGE=True,
        ENABLE_FAST_FORWARD=True,
        ALLOW_CREATE_FROM=None,
        MAX_FILE_SIZE=10 * 1024 * 1024, # 10MB default
    )

    # Load from environment variables with prefix XCHANGE_
    # e.g. XCHANGE_MONGO_URI
    app.config.from_prefixed_env(prefix='XCHANGE')

    # Normalize boolean values (env vars are loaded as strings if not valid JSON)
    for key in ['ENABLE_ADMIN_UI', 'ENABLE_UNLIMITED_USAGE', 'ENABLE_UNLIMITED_AGE', 'ENABLE_FAST_FORWARD']:
        val = app.config.get(key)
        if isinstance(val, str):
            if val.lower() in ['true', '1', 'yes']:
                app.config[key] = True
            elif val.lower() in ['false', '0', 'no']:
                app.config[key] = False

    # Process ALLOW_CREATE_FROM (CSV string to list)
    acf = app.config.get('ALLOW_CREATE_FROM')
    if acf and isinstance(acf, str):
        hosts = [h.strip() for h in acf.split(',') if h.strip()]
        app.config['ALLOW_CREATE_FROM'] = hosts
    elif not acf:
        app.config['ALLOW_CREATE_FROM'] = []

    # Local Assets for API Docs
    app.config['SWAGGER_UI_BUNDLE_JS'] = '/assets/swagger-ui-bundle.js'
    app.config['SWAGGER_UI_CSS'] = '/assets/swagger-ui.css'
    app.config['SWAGGER_UI_STANDALONE_PRESET_JS'] = '/assets/swagger-ui-standalone-preset.js'

    client = MongoClient(
        host=app.config['MONGO_HOST'],
        port=app.config['MONGO_PORT'],
        username=app.config['MONGO_USER'],
        password=app.config['MONGO_PASSWORD'],
    )
    app.db = client.get_database(name=app.config['MONGO_DBNAME'])

    # Create TTL index for expires_at (MongoDB will delete documents after the timestamp)
    app.db.items.create_index("expires_at", expireAfterSeconds=0)

    app.register_blueprint(frontend_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(admin_bp)

    # add module to allow compression of replies
    Compress(app)

    return app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
