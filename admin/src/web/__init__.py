from flask import Flask, render_template
from flask_debugtoolbar import DebugToolbarExtension

from core.database import db
from core.utils.bcrypt import bcrypt

from .config import get_current_config
from .controllers import auth_bp, feature_flag_bp, tag_bp, user_bp, user_management_bp
from .handlers import error
from .utils.auth import (
    get_user_role_name,
    has_permission,
    is_authenticated,
    is_system_admin,
)
from .utils.hooks import hook_admin_maintenance


def create_app(env="development", static_folder="../../static"):
    app = Flask(__name__, static_folder=static_folder)
    app.config.from_object(get_current_config(env))

    if app.config.get("DEBUG", False):
        DebugToolbarExtension(app)

    # Inicializar extensiones
    bcrypt.init_app(app)
    db.init_app(app)

    # Rutas
    @app.route("/")
    def home():
        return render_template("home.html")

    # Hooks
    app.before_request(hook_admin_maintenance)

    # Blueprints
    app.register_blueprint(user_management_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(tag_bp)
    app.register_blueprint(feature_flag_bp)
    app.register_blueprint(auth_bp)

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

    # TODO: Eliminar
    @app.cli.command("delete-tag")
    def delete_tag_command():
        from core.services import delete_tag

        delete_tag(1)

    # TODO: Eliminar
    @app.cli.command("paginated_tag")
    def paginated_tag_command():
        from core.services import get_paginated_tags

        print(get_paginated_tags(1, "name", "asc"))

        print(get_paginated_tags(1, "name", "dsc"))

    # TODO: Eliminar
    @app.cli.command("update_site")
    def update_site_command():
        from core.services import update_historic_site

        body = {
            "name": "Updated Obalisco",
            "brief_description": "Updated brief decription",
            "full_description": "Updated full description",
            "latitude": 1111111,
            "longitude": 22222,
            "inauguration_year": 2025,
            "is_visible": True,
            "city_id": 2,
            "conservation_state_id": 1,
            "category_id": 1,
            "tag_ids": [1],
            "historic_site_id": 1,
        }
        update_historic_site(body)

    # Métodos de jinja
    app.jinja_env.globals.update(is_authenticated=is_authenticated)
    app.jinja_env.globals.update(has_permission=has_permission)
    app.jinja_env.globals.update(is_system_admin=is_system_admin)
    app.jinja_env.globals.update(get_user_role_name=get_user_role_name)

    # Error handlers
    app.register_error_handler(404, error.not_found)
    app.register_error_handler(500, error.internal_server_error)
    app.register_error_handler(401, error.unauthorized)
    app.register_error_handler(403, error.forbidden)

    return app
