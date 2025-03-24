from src.utils import sqlalchemy
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource as FlaskResource


class BaseResource(FlaskResource):
    """An abstract base class for Model Resource.."""

    db: SQLAlchemy

    def __init__(self):
        super().__init__()
        self.db = sqlalchemy.SQLAlchemy.get_instance()
