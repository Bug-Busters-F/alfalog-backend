from src.utils.sqlalchemy import SQLAlchemy

from flask import Flask
from flask_restful import Api


def create_app():
    """Create Flask app."""
    app = Flask(__name__)
    app.config.from_prefixed_env()  # load all the env vars prefixed with 'FLASK_'
    app.config.from_prefixed_env("APP")  # load all the env vars prefixed with 'APP_'
    # app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY")
    # app.config["SESSION_TYPE"] = os.environ.get("FLASK_SESSION_TYPE")

    # init database/sqlalchemy connection
    SQLAlchemy.get_instance(app)

    api: Api = create_api(app)

    register_blueprints(app)

    # Add API resources.
    add_resources(api)

    return app


def create_api(app: Flask) -> Api:
    """Initialize the API instance."""
    api = Api(app)

    return api


def register_blueprints(app: Flask) -> None:
    """Register blueprints (routes) into the app."""

    from src.core.main import main

    app.register_blueprint(main)


def add_resources(api: Api) -> None:
    """Load the resources into the API."""

    # User resources
    from src.users.resources import User, Users

    api.add_resource(Users, "/api/users/")
    api.add_resource(User, "/api/users/<int:id>")
