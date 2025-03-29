from flask import Blueprint, request
from flask_restful import marshal_with

from .request import valor_agregado_args
from .fields import valor_agregado_fields
from src.transacoes.model import TransacaoModel
from src.ufs.model import UFModel
from src.utils.sqlalchemy import SQLAlchemy

main = Blueprint("main", __name__)


@main.route("/api/valor_agregado", methods=["POST"])
@marshal_with(valor_agregado_fields)
def valor_agregado():
    # input validation
    args = valor_agregado_args.parse_args(strict=True)

    db = SQLAlchemy.get_instance()

    entries = (
        db.session.query(
            TransacaoModel,
            (TransacaoModel.valor / TransacaoModel.peso).label("valor_agregado"),
        )
        .join(UFModel)
        .filter(UFModel.id == args["uf_id"], TransacaoModel.ano == args["ano"])
        .order_by(db.desc("valor_agregado"))
        .all()
    )

    return entries
