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

    # Pais resources
    from src.paises.resources import Paises, Pais

    api.add_resource(Paises, "/api/paises", "/api/paises/")
    api.add_resource(Pais, "/api/paises/<int:id>")

    # UF resources
    from src.ufs.resources import UFs, UF

    api.add_resource(UFs, "/api/ufs", "/api/ufs/")
    api.add_resource(UF, "/api/ufs/<int:id>")

    # SH6 resources
    from src.sh6s.resources import SH6s, SH6

    api.add_resource(SH6s, "/api/sh6s", "/api/sh6s/")
    api.add_resource(SH6, "/api/sh6s/<int:id>")

    # SH4 resources
    from src.sh4s.resources import SH4s, SH4

    api.add_resource(SH4s, "/api/sh4s", "/api/sh4s/")
    api.add_resource(SH4, "/api/sh4s/<int:id>")

    # NCM resources
    from src.ncms.resources import NCMs, NCM

    api.add_resource(NCMs, "/api/ncms", "/api/ncms/")
    api.add_resource(NCM, "/api/ncms/<int:id>")

    # Transacao resources
    from src.transacoes.resources import Transacoes, Transacao

    api.add_resource(Transacoes, "/api/transacoes", "/api/transacoes/")
    api.add_resource(Transacao, "/api/transacoes/<int:id>")
