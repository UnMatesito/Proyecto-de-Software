from flask import Flask, render_template
from flask_debugtoolbar import DebugToolbarExtension

from core.database import db
from core.utils.bcrypt import bcrypt

from .config import get_current_config
from .controllers import auth as auth_bp
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

    # Blueprints
    app.register_blueprint(auth_bp.bp)

    # Commands
    @app.cli.command("reset-db")
    def reset_db_command():
        from core.database import reset_db

        reset_db(app)

    @app.cli.command("seed-db")
    def seed_db_command():
        from core.seeds import run as seed_db

        seed_db()

    # Error handlers
    app.register_error_handler(404, error.not_found)
    app.register_error_handler(500, error.internal_server_error)
    app.register_error_handler(401, error.unauthorized)

    return app
