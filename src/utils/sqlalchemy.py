from src.core.base import BaseModel

from flask import Flask, current_app
from flask_sqlalchemy import SQLAlchemy as OriginalSQLAlchemy


class SQLAlchemy:
    """Singleton for a (original) SQLAlchemy instance."""

    _instance: OriginalSQLAlchemy = None

    @staticmethod
    def get_instance(app: Flask = None) -> OriginalSQLAlchemy:
        """Return the existing instance of (original) SQLALchemy class or create the first one.

        Args:
            app (Flask, optional): Flask app instance. Defaults to None.

        Raises:
            RuntimeError: if SQLAlchemy not initialized.

        Returns:
            flask_sqlalchemy.SQLAlchemy: DB connection.
        """
        if SQLAlchemy._instance is None:
            if not isinstance(app, Flask):
                raise RuntimeError(
                    "Cannot connect to the database. Missing app context."
                )
            SQLAlchemy._instance = SQLAlchemy._create_sql_alchemist(app)

        return SQLAlchemy._instance

    @staticmethod
    def _create_sql_alchemist(app: Flask) -> OriginalSQLAlchemy:
        """Create a (original) SQLAlchemy instance."""
        db = OriginalSQLAlchemy(model_class=BaseModel)

        app.config["SQLALCHEMY_DATABASE_URI"] = (
            f"mysql://{app.config['DB_USER']}:{app.config['DB_PASS']}"
            f"@{app.config['DB_HOST']}:{app.config['DB_PORT']}/{app.config['DB_NAME']}"
        )
        db.init_app(app)

        return db
