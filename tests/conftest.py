import pytest
from flask import Flask
from dotenv import load_dotenv
from src.utils.sqlalchemy import SQLAlchemy
from src import create_app

load_dotenv()


@pytest.fixture(scope="session")
def app():
    """Create a new Flask app instance for each test."""
    _app = create_app()
    _app.config.update(
        {
            "TESTING": True,
            "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        }
    )

    ctx = _app.app_context()
    ctx.push()

    yield _app

    # ctx.pop()


@pytest.fixture(scope="session")
def db(app: Flask):
    """Database fixture with session scope"""
    _db = SQLAlchemy.get_instance(app)

    _db.drop_all()
    _db.create_all()

    yield _db

    _db.drop_all()
    _db.create_all()


@pytest.fixture(scope="function")
def client(app):
    """Test client fixture"""
    return app.test_client()


@pytest.fixture(scope="function")
def session(db):
    """Creates a new database session for each test"""
    connection = db.engine.connect()
    transaction = connection.begin()

    session = db.create_session(bind=connection)
    db.session = session

    yield session

    session.close()
    connection.close()


@pytest.fixture(autouse=True)
def auto_rollback(session):
    yield
    session.rollback()
