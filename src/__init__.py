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

    # URF resources
    from src.urfs.resources import URFs, URF

    api.add_resource(URFs, "/api/urfs", "/api/urfs/")
    api.add_resource(URF, "/api/urfs/<int:id>")

    # Via resources
    from src.vias.resources import Vias, Via

    api.add_resource(Vias, "/api/vias", "/api/vias/")
    api.add_resource(Via, "/api/vias/<int:id>")

    # Unidades Estatísticas resources
    from src.ues.resources import UEs, UE

    api.add_resource(UEs, "/api/ues", "/api/ues/")
    api.add_resource(UE, "/api/ues/<int:id>")
