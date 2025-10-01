import os

import pytest
from dotenv import load_dotenv

from core.database import db
from core.models import City, HistoricSite
from src.web import create_app

# Load environment variables
load_dotenv()


@pytest.fixture(scope="session")
def app():
    """Create application for testing."""
    app = create_app()

    # Use the same database URL as development
    database_url = os.getenv("DATABASE_URL")

    app.config.update(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": database_url,
            "WTF_CSRF_ENABLED": False,
            "SECRET_KEY": os.getenv("SECRET_KEY"),
        }
    )

    with app.app_context():
        yield app


@pytest.fixture(scope="session")
def _db(app):
    """Create database for testing."""
    db.create_all()

    # Ensure the tables are created
    yield db

    db.session.rollback()


@pytest.fixture(scope="function")
def db_session(app, _db):
    """Create a database session for a test that rolls back all changes."""
    with app.app_context():
        connection = _db.engine.connect()
        transaction = connection.begin()

        # Bind a session to this connection
        _db.session.configure(bind=connection, autoflush=False, expire_on_commit=False)

        yield _db.session

        # Cleanup - rollback everything the test did
        transaction.rollback()
        connection.close()
        _db.session.remove()


@pytest.fixture
def client(app):
    """Create a test client."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create a test runner for CLI commands."""
    return app.test_cli_runner()
