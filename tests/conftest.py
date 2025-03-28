import os

# from flask_sqlalchemy import SQLAlchemy
from src.utils.sqlalchemy import SQLAlchemy
import pytest
from src import create_app

fapp = create_app()
fapp.config.update(
    {
        "TESTING": True,
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
    }
)

db = SQLAlchemy.get_instance(fapp)
# db = SQLAlchemy()
# db.init_app(fapp)


@pytest.fixture()
def app():
    """Create a new Flask app instance for each test."""
    global db, fapp

    # Create the database schema for testing (if needed)
    with fapp.app_context():
        db.create_all()  # Create tables

    yield fapp

    # Clean up after test, ensure we're in fapp context
    with fapp.app_context():
        # Clean up after test
        db.session.remove()
        db.drop_all()
        # Create tables
        db.create_all()


@pytest.fixture()
def client(app):
    """Flask test client to send HTTP requests."""
    return app.test_client()
