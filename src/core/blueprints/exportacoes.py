import marshal
from flask import Blueprint, request
from flask_restful import marshal_with
from ..request import valor_agregado_args, cargas_movimentadas_args
from ..fields import cargas_movimentadas_fields, valor_agregado_fields
from src.exportacoes.model import ExportacaoModel
from src.ufs.model import UFModel
from src.utils.sqlalchemy import SQLAlchemy


exportacoes = Blueprint("exportacoes", __name__)


@exportacoes.route("/api/exportacoes/valor-agregado", methods=["POST"])
@marshal_with(valor_agregado_fields)
def valor_agregado():
    """Retrieve Transações incluindo seu valor agregado."""
    # input validation
    args = valor_agregado_args.parse_args(strict=True)

    db = SQLAlchemy.get_instance()

    entries = (
        db.session.query(ExportacaoModel)
        .join(UFModel)
        .filter(UFModel.id == args["uf_id"], ExportacaoModel.ano == args["ano"])
        .order_by(ExportacaoModel.valor_agregado.desc())
        .all()
    )

    return entries


@exportacoes.route("/api/exportacoes/cargas-movimentadas", methods=["POST"])
@marshal_with(cargas_movimentadas_fields)
def cargas_movimentadas():
    """Inclui dados referente as cargas movimentadas."""
    # input validation
    args = cargas_movimentadas_args.parse_args(strict=True)

    db = SQLAlchemy.get_instance()

    entries = (
        db.session.query(
            ExportacaoModel.id,
            ExportacaoModel.peso,
            ExportacaoModel.ncm_id,
        )
        .join(UFModel)
        .filter(UFModel.id == args["uf_id"], ExportacaoModel.ano == args["ano"])
        .order_by(db.desc(ExportacaoModel.peso))
        .all()
    )

    return entries
