from flask_restful import marshal_with, abort
from src.core.resources import BaseResource
from src.ufs.model import UFModel
from .model import BalancaModel
from .fields import model_fields
from .request import model_args


class Balancas(BaseResource):
    @marshal_with(model_fields)
    def get(self):
        entries = self.db.session.query(BalancaModel).all()
        return entries

    @marshal_with(model_fields)
    def post(self):
        args = model_args.parse_args(strict=True)
        uf = self.db.session.get(UFModel, args["id_uf"])
        if not uf:
            abort(404, message="UF não encontrada.")

        entry = BalancaModel(ano=args["ano"], valor=args["valor"], uf=uf)
        self.db.session.add(entry)
        self.db.session.commit()
        return entry, 201


class Balanca(BaseResource):
    @marshal_with(model_fields)
    def get(self, id):
        entry = self.db.session.query(BalancaModel).filter_by(id=id).first()
        if not entry:
            abort(404, message="Registro não encontrado.")
        return entry

    @marshal_with(model_fields)
    def put(self, id):
        args = model_args.parse_args(strict=True)
        entry = self.db.session.query(BalancaModel).filter_by(id=id).first()
        if not entry:
            abort(404, message="Registro não encontrado.")

        uf = self.db.session.get(UFModel, args["id_uf"])
        if not uf:
            abort(404, message="UF não encontrada.")

        entry.ano = args["ano"]
        entry.valor = args["valor"]
        entry.uf = uf

        self.db.session.commit()
        return entry, 200

    @marshal_with(model_fields)
    def delete(self, id):
        entry = self.db.session.query(BalancaModel).filter_by(id=id).first()
        if not entry:
            abort(404, message="Registro não encontrado.")
        self.db.session.delete(entry)
        self.db.session.commit()
        return None, 204
