import pytest
from src.web import create_app
from src.core.database import db
from src.core.services.user_service import create_user, block_user, unlock_user, delete_user, change_password, assign_role
from src.core.models import User

@pytest.fixture
def app():
    app = create_app("testing") 
    with app.app_context():
        yield app
""""
def test_create_user(app):
    user = create_user(email="a@test.com", password="1234")
    assert user.email == "a@test.com"
    assert user.password_hash is not None
"""
def test_block_user(app):
    block_user(1)
    u = User.query.get(1)
    assert u.blocked is True
