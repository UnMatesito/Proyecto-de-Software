from core.database import db
from core.models import User


def list_users():
    return User.query.all()


def get_user_by_id(user_id):
    return User.query.get(user_id)


def create_user(email, username, password_hash):
    user = User(email=email, username=username, password_hash=password_hash)
    db.session.add(user)
    db.session.commit()
    return user
