from flask import Flask, render_template
from flask_debugtoolbar import DebugToolbarExtension
from src.core.db import db
from src.web.config import current_config
from src.web.controllers.issue import issue_bp

from .handlers import error


def create_app(env="development", static_folder="../../static"):
    app = Flask(__name__, static_folder=static_folder)
    app.config.from_object(current_config)

    if app.config.get("DEBUG", False):
        DebugToolbarExtension(app)

    # Inicializar base de datos
    db.init_app(app)

    with app.app_context():
        db.create_all()

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db.session.remove()

    # Rutas
    @app.route("/")
    def home():
        return render_template("home.html")

    # Blueprints

    # Error handlers
    app.register_error_handler(404, error.not_found)
    app.register_error_handler(500, error.internal_server_error)
    app.register_error_handler(401, error.unauthorized)

    return app
