from src.core.resources import BaseResource
from src.ncms.model import NCMModel
from src.paises.model import PaisModel
from src.ues.model import UEModel
from src.ufs.model import UFModel
from src.urfs.model import URFModel
from src.utils import sqlalchemy
from src.vias.model import ViaModel
from .model import ExportacaoModel
from .fields import model_fields
from .request import model_args

from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, marshal_with, abort
from werkzeug import exceptions


class Exportacoes(BaseResource):
    """Model's collection routing (controller)."""

    @marshal_with(model_fields)
    def get(self):
        """Get all entries."""
        entries = self.db.session.query(ExportacaoModel).all()
        return entries

    @marshal_with(model_fields)
    def post(self):
        """Create new entry."""
        # input validation
        args = model_args.parse_args(strict=True)

        # Check whether codigo already exists
        existing_entry = (
            self.db.session.query(ExportacaoModel)
            .filter_by(codigo=args["codigo"])
            .first()
        )
        if existing_entry:
            return abort(422, message="Já existe uma Exportacao com esse código.")

        ncm = self.db.session.get(NCMModel, args["ncm_id"])
        if not ncm:
            return abort(404, message="NCM não encontrado.")
        ue = self.db.session.get(UEModel, args["ue_id"])
        if not ue:
            return abort(404, message="UE não encontrado.")
        pais = self.db.session.get(PaisModel, args["pais_id"])
        if not pais:
            return abort(404, message="País não encontrado.")
        uf = self.db.session.get(UFModel, args["uf_id"])
        if not uf:
            return abort(404, message="UF não encontrado.")
        via = self.db.session.get(ViaModel, args["via_id"])
        if not via:
            return abort(404, message="Via não encontrado.")
        urf = self.db.session.get(URFModel, args["urf_id"])
        if not urf:
            return abort(404, message="URF não encontrado.")

        entry = ExportacaoModel(
            codigo=args["codigo"],
            nome=args["nome"],
            ano=args["ano"],
            mes=args["mes"],
            quantidade=args["quantidade"],
            peso=args["peso"],
            valor=args["valor"],
            ncm=ncm,
            ue=ue,
            pais=pais,
            uf=uf,
            via=via,
            urf=urf,
        )
        self.db.session.add(entry)
        self.db.session.commit()
        return entry, 201


class Exportacao(BaseResource):
    """Model's routing (controller)."""

    @marshal_with(model_fields)
    def get(self, id):
        entry = self.db.session.query(ExportacaoModel).filter_by(id=id).first()
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

        entry = self.db.session.query(ExportacaoModel).filter_by(id=id).first()
        if not entry:
            abort(404, message="Nenhum registro encontrado.")

        # Check whether codigo already exists
        existing_entry = (
            self.db.session.query(ExportacaoModel)
            .filter_by(codigo=args["codigo"])
            .first()
        )
        if existing_entry and existing_entry.id != entry.id:
            return abort(422, message="Já existe uma Exportacao com esse código.")

        # FKs
        ncm = self.db.session.get(NCMModel, args["ncm_id"])
        if not ncm:
            return abort(404, message="NCM não encontrado.")
        ue = self.db.session.get(UEModel, args["ue_id"])
        if not ue:
            return abort(404, message="UE não encontrado.")
        pais = self.db.session.get(PaisModel, args["pais_id"])
        if not pais:
            return abort(404, message="País não encontrado.")
        uf = self.db.session.get(UFModel, args["uf_id"])
        if not uf:
            return abort(404, message="UF não encontrado.")
        via = self.db.session.get(ViaModel, args["via_id"])
        if not via:
            return abort(404, message="Via não encontrado.")
        urf = self.db.session.get(URFModel, args["urf_id"])
        if not urf:
            return abort(404, message="URF não encontrado.")

        entry.codigo = args["codigo"]
        entry.nome = args["nome"]
        entry.ano = args["ano"]
        entry.mes = args["mes"]
        entry.quantidade = args["quantidade"]
        entry.peso = args["peso"]
        entry.valor = args["valor"]
        entry.ncm = ncm
        entry.ue = ue
        entry.pais = pais
        entry.uf = uf
        entry.via = via
        entry.urf = urf
        self.db.session.commit()
        return None, 204

    @marshal_with(model_fields)
    def delete(self, id):
        entry = self.db.session.query(ExportacaoModel).filter_by(id=id).first()
        if not entry:
            abort(404, message="Nenhum registro encontrado.")
        self.db.session.delete(entry)
        self.db.session.commit()
        return None, 204
