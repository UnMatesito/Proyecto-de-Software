from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import  DeclarativeBase

db = SQLAlchemy()

def init_db(app):

    db.init_app(app)

    config_db(app)

    with app.app_context():
        db.create_all()

    return app


def config_db(app):
    @app.teardown_appcontext
    def close_db_session(exception=None):
        db.session.remove()

    return app


def reset_db(app):
    with app.app_context():
        db.drop_all()
        db.create_all()