from src.core.resources import BaseResource
from src.utils import sqlalchemy
from .model import URFModel
from .fields import model_fields
from .request import model_args

from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, marshal_with, abort
from werkzeug import exceptions


class URFs(BaseResource):
    """Model's collection routing (controller)."""

    @marshal_with(model_fields)
    def get(self):
        """Get all entries."""
        entries = self.db.session.query(URFModel).all()
        return entries

    @marshal_with(model_fields)
    def post(self):
        """Create new entry."""
        # input validation

        args = model_args.parse_args(strict=True)

        # Check whether codigo already exists
        existing_entry = (
            self.db.session.query(URFModel).filter_by(codigo=args["codigo"]).first()
        )
        if existing_entry:
            return abort(422, message="Já existe uma URF com esse código.")

        entry = URFModel(nome=args["nome"], codigo=args["codigo"])
        self.db.session.add(entry)
        self.db.session.commit()

        return entry, 201


class URF(BaseResource):
    """Model's routing (controller)."""

    @marshal_with(model_fields)
    def get(self, id):
        entry = self.db.session.query(URFModel).filter_by(id=id).first()
        if not entry:
            abort(404, message="Nenhum registro encontrado.")
        return entry

    @marshal_with(model_fields)
    def put(self, id):
        """Update an entry.

        Args:
            id (int): Entry ID.

        Returns:
            str: Entry data in JSON format.
        """
        # input validation
        args = model_args.parse_args(
            strict=True,
            http_error_code=422,
        )

        entry = self.db.session.query(URFModel).filter_by(id=id).first()
        if not entry:
            abort(404, message="Nenhum registro encontrado.")

        # Check whether codigo already exists
        existing_entry = (
            self.db.session.query(URFModel).filter_by(codigo=args["codigo"]).first()
        )
        if existing_entry and existing_entry.id != entry.id:
            return abort(422, message="Já existe uma URF com esse código.")

        entry.nome = args["nome"]
        entry.codigo = args["codigo"]
        self.db.session.commit()
        return None, 204

    @marshal_with(model_fields)
    def delete(self, id):
        entry = self.db.session.query(URFModel).filter_by(id=id).first()
        if not entry:
            abort(404, message="Nenhum registro encontrado.")
        self.db.session.delete(entry)
        self.db.session.commit()
        return None, 204
