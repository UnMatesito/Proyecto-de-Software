from flask import Flask, render_template, session
from flask_debugtoolbar import DebugToolbarExtension

from core.database import db
from core.models import User
from core.utils.bcrypt import bcrypt

from .config import get_current_config
from .controllers import user_bp, user_management_bp, feature_flag_bp
from .handlers import error


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

    # TODO: Eliminar
    @app.route("/fake-login/<string:email>")
    def fake_login(email):
        """
        Login falso para pruebas: simula que el usuario con ese email inició sesión
        """
        # Buscar el usuario en la DB
        user = User.query.filter_by(email=email).first()
        if not user:
            return f"Usuario con email {email} no existe", 404

        # Simular login guardando en session
        session["user_id"] = user.id

        return f"Sesión simulada como {user.email} (rol_id={user.role_id})"

    # Blueprints
    app.register_blueprint(user_management_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(feature_flag_bp)

    # Commands
    @app.cli.command("reset-db")
    def reset_db_command():
        from core.database import reset_db

        reset_db(app)

    @app.cli.command("seed-db")
    def seed_db_command():
        from core.seeds import run as seed_db

        seed_db()

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

    # Error handlers
    app.register_error_handler(404, error.not_found)
    app.register_error_handler(500, error.internal_server_error)
    app.register_error_handler(401, error.unauthorized)

    return app
