import marshal
from flask import Blueprint, request
from flask_restful import marshal_with
from .request import valor_agregado_args, cargas_movimentadas_args
from .fields import valor_agregado_fields, cargas_movimentadas_fields
from src.importacoes.model import ImportacaoModel
from src.ufs.model import UFModel
from src.utils.sqlalchemy import SQLAlchemy


importacoes = Blueprint("importacoes", __name__)


@importacoes.route("/api/importacoes/valor-agregado", methods=["POST"])
@marshal_with(valor_agregado_fields)
def valor_agregado():
    """Retrieve Transações incluindo seu valor agregado."""
    # input validation
    args = valor_agregado_args.parse_args(strict=True)

    db = SQLAlchemy.get_instance()

    entries = (
        db.session.query(ImportacaoModel)
        .join(UFModel)
        .filter(UFModel.id == args["uf_id"], ImportacaoModel.ano == args["ano"])
        .order_by(ImportacaoModel.valor_agregado.desc())
        .all()
    )

    return entries


@importacoes.route("/api/importacoes/cargas-movimentadas", methods=["POST"])
@marshal_with(cargas_movimentadas_fields)
def cargas_movimentadas():
    """Inclui dados referente as cargas movimentadas."""
    # input validation
    args = cargas_movimentadas_args.parse_args(strict=True)

    db = SQLAlchemy.get_instance()

    entries = (
        db.session.query(
            ImportacaoModel.id,
            ImportacaoModel.peso,
            ImportacaoModel.ncm_id,
        )
        .join(UFModel)
        .filter(UFModel.id == args["uf_id"], ImportacaoModel.ano == args["ano"])
        .order_by(db.desc(ImportacaoModel.peso))
        .all()
    )

    return entries
