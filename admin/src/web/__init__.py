from flask import Flask

from authlib.integrations.flask_client import OAuth
import os
from core.storage import storage
from core.database import db
from core.utils.bcrypt import bcrypt
from flask_session import Session
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from .config import get_current_config
from .controllers import (
    auth_bp,
    city_bp,
    feature_flag_bp,
    main_bp,
    site_bp,
    site_history_bp,
    tag_bp,
    user_bp,
    user_management_bp,
    review_bp
)

from .handlers import error
from .utils.auth import (
    get_user_role_name,
    has_permission,
    is_authenticated,
    is_system_admin,
    is_validated_site, get_current_user,
)
from .utils.hooks import hook_admin_maintenance

session = Session()
oauth = OAuth()
jwt = JWTManager()

def create_app(env="development", static_folder="../../static"):
    app = Flask(__name__, static_folder=static_folder)
    app.config.from_object(get_current_config(env))

    if app.config.get("DEBUG", False):
        from flask_debugtoolbar import DebugToolbarExtension

        DebugToolbarExtension(app)

    # Inicializar extensiones
    bcrypt.init_app(app)
    db.init_app(app)
    session.init_app(app)
    storage.init_app(app)
    CORS(
        app,
        resources={r"/api/*": {"origins": app.config["CORS_ORIGINS"]}},
        supports_credentials=True
    )

    jwt.init_app(app)
    oauth.init_app(app)

    oauth.register(
        name='google',
        client_id=app.config.get('GOOGLE_CLIENT_ID'),
        client_secret=app.config.get('GOOGLE_CLIENT_SECRET'),
        authorize_url='https://accounts.google.com/o/oauth2/v2/auth?prompt=select_account&',
        access_token_url='https://oauth2.googleapis.com/token',
        client_kwargs={'scope': 'openid email profile'},
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration'
    )

    from .controllers import (
        auth_bp, city_bp, feature_flag_bp, main_bp, site_bp,
        site_history_bp, tag_bp, user_bp, user_management_bp
    )
    from .controllers.api import api_bp

    # Registrar listeners de auditoría
    from core import audit

    # Hooks
    app.before_request(hook_admin_maintenance)

    # Blueprints portal administrativo
    app.register_blueprint(main_bp)
    app.register_blueprint(user_management_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(tag_bp)
    app.register_blueprint(feature_flag_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(site_bp)
    app.register_blueprint(city_bp)
    app.register_blueprint(site_history_bp)
    app.register_blueprint(review_bp)

    # Blueprints API
    app.register_blueprint(api_bp, url_prefix="/api")

    # Commands
    @app.cli.command("reset-db")
    def reset_db_command():
        from core.database import reset_db

        reset_db(app)

    @app.cli.command("seed-db")
    def seed_db_command():
        import os

        from core.seeds import run as seed_db

        env = os.getenv("FLASK_ENV", "production")

        seed_db(env)

    # Inicialización automática para producción
    with app.app_context():
        if env == "production":
            from core.database import reset_db
            from core.seeds import run as seed_db

            # Borra y crea la base de datos
            reset_db(app)

            # Corre los seeds
            seed_db(app)

    # Métodos de jinja
    app.jinja_env.globals.update(is_authenticated=is_authenticated)
    app.jinja_env.globals.update(has_permission=has_permission)
    app.jinja_env.globals.update(is_system_admin=is_system_admin)
    app.jinja_env.globals.update(get_user_role_name=get_user_role_name)
    app.jinja_env.globals.update(is_validated_site=is_validated_site)
    app.jinja_env.globals.update(get_current_user=get_current_user)

    # Error handlers
    app.register_error_handler(404, error.not_found)
    app.register_error_handler(500, error.internal_server_error)
    app.register_error_handler(401, error.unauthorized)
    app.register_error_handler(403, error.forbidden)

    return app
