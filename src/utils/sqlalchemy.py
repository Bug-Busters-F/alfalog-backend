from src.core.base import BaseModel

from flask import Flask, current_app
from flask_sqlalchemy import SQLAlchemy as OriginalSQLAlchemy


class SQLAlchemy:
    """Singleton for making synchronous database connections."""

    _instance: OriginalSQLAlchemy = None

    @classmethod
    def get_instance(cls, app: Flask = None) -> OriginalSQLAlchemy:
        """Return a database connection.

        Args:
            app (Flask, optional): Flask app instance. Defaults to None.

        Raises:
            RuntimeError: if SQLAlchemy not initialized.

        Returns:
            flask_sqlalchemy.SQLAlchemy: DB connection.
        """
        if cls._instance is None:
            if not isinstance(app, Flask):
                raise RuntimeError(
                    "Cannot connect to the database. Missing app context."
                )
            cls._instance = cls._create_sql_alchemist(app)

        return cls._instance

    @classmethod
    def _create_sql_alchemist(cls, app: Flask) -> OriginalSQLAlchemy:
        """Make a database connection."""
        db = OriginalSQLAlchemy(model_class=BaseModel)
        cls._build_uri(app)
        db.init_app(app)

        return db

    def _build_uri(app: Flask) -> None:
        app.config["SQLALCHEMY_DATABASE_URI"] = (
            f"mysql://{app.config['DB_USER']}:{app.config['DB_PASS']}"
            f"@{app.config['DB_HOST']}:{app.config['DB_PORT']}/{app.config['DB_NAME']}"
        )
