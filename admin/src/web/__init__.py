from flask import Flask, render_template
from flask_debugtoolbar import DebugToolbarExtension

from src.web.config import current_config

from .handlers import error


def create_app(env="development", static_folder="../../static"):
    app = Flask(__name__, static_folder=static_folder)
    app.config.from_object(current_config)

    if app.config.get("DEBUG", False):
        DebugToolbarExtension(app)

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
