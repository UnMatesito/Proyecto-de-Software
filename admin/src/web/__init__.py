from flask import Flask, render_template
from flask_debugtoolbar import DebugToolbarExtension

from core.database import db
from core.utils.bcrypt import bcrypt

from .config import get_current_config
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

    # Commands
    @app.cli.command("reset-db")
    def reset_db_command():
        from core.database import reset_db

        reset_db(app)

    @app.cli.command("seed-db")
    def seed_db_command():
        from core.seeds import run as seed_db

        seed_db()

    @app.cli.command("delete-tag")
    def delete_tag_command():
        from core.services import delete_tag

        delete_tag(1)

    @app.cli.command("paginated_tag")
    def paginated_tag_command():
        from core.services import get_paginated_tags

        print(get_paginated_tags(1, "name", "asc"))

        print(get_paginated_tags(1, "name", "dsc"))

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
            "historic_site_id": 1
        }
        update_historic_site(body)
    # Error handlers
    app.register_error_handler(404, error.not_found)
    app.register_error_handler(500, error.internal_server_error)
    app.register_error_handler(401, error.unauthorized)

    return app
