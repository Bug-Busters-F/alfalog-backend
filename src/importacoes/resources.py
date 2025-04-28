from src.core.resources import BaseResource
from src.ncms.model import NCMModel
from src.paises.model import PaisModel
from src.ues.model import UEModel
from src.ufs.model import UFModel
from src.urfs.model import URFModel
from src.utils import sqlalchemy
from src.vias.model import ViaModel
from .model import ImportacaoModel
from .fields import model_fields
from .request import model_args

from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, marshal_with, abort
from werkzeug import exceptions


class Importacoes(BaseResource):
    """Model's collection routing (controller)."""

    @marshal_with(model_fields)
    def get(self):
        """Get all entries."""
        entries = self.db.session.query(ImportacaoModel).all()
        return entries

    @marshal_with(model_fields)
    def post(self):
        """Create new entry."""
        # input validation
        args = model_args.parse_args(strict=True)

        entry = ImportacaoModel(
            ano=args["ano"],
            mes=args["mes"],
            peso=args["peso"],
            valor=args["valor"],
        )

        if "ncm_id" in args:
            ncm = self.db.session.get(NCMModel, args["ncm_id"])
            if not ncm:
                return abort(404, message="NCM não encontrado.")
            entry.ncm = ncm
        if "ue_id" in args:
            ue = self.db.session.get(UEModel, args["ue_id"])
            if not ue:
                return abort(404, message="UE não encontrado.")
            entry.ue = ue
        if "pais_id" in args:
            pais = self.db.session.get(PaisModel, args["pais_id"])
            if not pais:
                return abort(404, message="País não encontrado.")
            entry.pais = pais
        if "uf_id" in args:
            uf = self.db.session.get(UFModel, args["uf_id"])
            if not uf:
                return abort(404, message="UF não encontrado.")
            entry.uf = uf
        if "via_id" in args:
            via = self.db.session.get(ViaModel, args["via_id"])
            if not via:
                return abort(404, message="Via não encontrado.")
            entry.via = via
        if "urf_id" in args:
            urf = self.db.session.get(URFModel, args["urf_id"])
            if not urf:
                return abort(404, message="URF não encontrado.")
            entry.urf = urf

        self.db.session.add(entry)
        self.db.session.commit()
        return entry, 201


class Importacao(BaseResource):
    """Model's routing (controller)."""

    @marshal_with(model_fields)
    def get(self, id):
        entry = self.db.session.query(ImportacaoModel).filter_by(id=id).first()
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
            http_error_code=400,
        )

        entry = self.db.session.query(ImportacaoModel).filter_by(id=id).first()
        if not entry:
            abort(404, message="Nenhum registro encontrado.")

        # FKs
        if "ncm_id" in args:
            ncm = self.db.session.get(NCMModel, args["ncm_id"])
            if not ncm:
                return abort(404, message="NCM não encontrado.")
            entry.ncm = ncm
        if "ue_id" in args:
            ue = self.db.session.get(UEModel, args["ue_id"])
            if not ue:
                return abort(404, message="UE não encontrado.")
            entry.ue = ue
        if "pais_id" in args:
            pais = self.db.session.get(PaisModel, args["pais_id"])
            if not pais:
                return abort(404, message="País não encontrado.")
            entry.pais = pais
        if "uf_id" in args:
            uf = self.db.session.get(UFModel, args["uf_id"])
            if not uf:
                return abort(404, message="UF não encontrado.")
            entry.uf = uf
        if "via_id" in args:
            via = self.db.session.get(ViaModel, args["via_id"])
            if not via:
                return abort(404, message="Via não encontrado.")
            entry.via = via
        if "urf_id" in args:
            urf = self.db.session.get(URFModel, args["urf_id"])
            if not urf:
                return abort(404, message="URF não encontrado.")
            entry.urf = urf

        entry.ano = args["ano"]
        entry.mes = args["mes"]
        entry.peso = args["peso"]
        entry.valor = args["valor"]
        self.db.session.commit()
        return None, 204

    @marshal_with(model_fields)
    def delete(self, id):
        entry = self.db.session.query(ImportacaoModel).filter_by(id=id).first()
        if not entry:
            abort(404, message="Nenhum registro encontrado.")
        self.db.session.delete(entry)
        self.db.session.commit()
        return None, 204
