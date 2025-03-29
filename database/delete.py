# Load environment variables from .env file
from dotenv import load_dotenv

load_dotenv()

from src import create_app

app = create_app()


from sqlalchemy_utils import database_exists
from src.utils.sqlalchemy import SQLAlchemy

mysql_uri = app.config["SQLALCHEMY_DATABASE_URI"]
if database_exists(mysql_uri):
    with app.app_context():
        db = SQLAlchemy.get_instance(app)
        db.drop_all()
