from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import  DeclarativeBase

class Base(DeclarativeBase):
    pass

db = SQLAlchemy()

def init_db(app):
    print("init_db")
    db.init_app(app)
    config(app)

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