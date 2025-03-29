import marshal
from flask import Blueprint, request
from flask_restful import marshal_with
from sqlalchemy import func
from .request import valor_agregado_args, cargas_movimentadas_args
from .fields import valor_agregado_fields, cargas_movimentadas_fields
from src.transacoes.model import TransacaoModel
from src.ufs.model import UFModel
from src.utils.sqlalchemy import SQLAlchemy

main = Blueprint("main", __name__)


@main.route("/api/valor_agregado", methods=["POST"])
@marshal_with(valor_agregado_fields)
def valor_agregado():
    """Retrieve Transações incluindo seu valor agregado."""
    # input validation
    args = valor_agregado_args.parse_args(strict=True)

    db = SQLAlchemy.get_instance()

    entries = (
        db.session.query(
            TransacaoModel,
            func.round(TransacaoModel.valor / TransacaoModel.peso, 2).label(
                "valor_agregado"
            ),
        )
        .join(UFModel)
        .filter(UFModel.id == args["uf_id"], TransacaoModel.ano == args["ano"])
        .order_by(db.desc("valor_agregado"))
        .all()
    )

    return entries


@main.route("/api/cargas_movimentadas", methods=["POST"])
@marshal_with(cargas_movimentadas_fields)
def cargas_movimentadas():
    """Inclui dados referente as cargas movimentadas."""
    # input validation
    args = cargas_movimentadas_args.parse_args(strict=True)

    db = SQLAlchemy.get_instance()

    entries = (
        db.session.query(
            TransacaoModel.id,
            TransacaoModel.peso,
            TransacaoModel.ncm_id,
        )
        .join(UFModel)
        .filter(UFModel.id == args["uf_id"], TransacaoModel.ano == args["ano"])
        .order_by(db.desc(TransacaoModel.peso))
        .all()
    )

    return entries
