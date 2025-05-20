# Load environment variables from .env file
from dotenv import load_dotenv

from src.utils import sqlalchemy

load_dotenv()


# App
from src import create_app
from src.somas.model import SomaModel

app = create_app()


# Create database
from sqlalchemy_utils import create_database, database_exists

mysql_uri = app.config["SQLALCHEMY_DATABASE_URI"]

if not database_exists(mysql_uri):
    create_database(mysql_uri)


# Create tables
from src.utils.sqlalchemy import SQLAlchemy

with app.app_context():
    db = SQLAlchemy.get_instance(app)
    db.create_all()
