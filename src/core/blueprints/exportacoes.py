import marshal
from flask import Blueprint, request
from flask_restful import marshal_with
from ..request import valor_agregado_args, cargas_movimentadas_args, vias_utilizadas_args, valor_agregado_geral_args
from ..fields import cargas_movimentadas_fields, valor_agregado_fields, vias_fields, valor_agregado_por_estado_fields
from src.exportacoes.model import ExportacaoModel
from src.ufs.model import UFModel
from src.vias.model import ViaModel
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


@exportacoes.route("/api/exportacoes/vias-utilizadas", methods=["POST"])
@marshal_with(vias_fields)
def vias_utilizadas():
    """Retorna as vias e a quantidade de vezes que foram usadas em um estado."""
    args = vias_utilizadas_args.parse_args(strict=True)

    db = SQLAlchemy.get_instance()

    entries = (
        db.session.query(
            db.func.count(ExportacaoModel.via_id).label("qtd"),
            ExportacaoModel.via_id.label("via_id")
        )
        .join(ViaModel, ExportacaoModel.via_id == ViaModel.id)
        .filter(ExportacaoModel.ano == args["ano"],ExportacaoModel.uf_id == args["uf_id"])
        .group_by(ExportacaoModel.via_id)
        .all()
    )

    return entries

    # comando p/ testes CMD
    # curl -X POST http://127.0.0.1:5000/api/exportacoes/vias-utilizadas -H "Content-Type: application/json" -d "{\"ano\": 2023, \"uf_id\": 12}"


@exportacoes.route("/api/exportacoes/valor-agregado/por-estado", methods=["POST"])
@marshal_with(valor_agregado_por_estado_fields)
def valor_agregado_por_estado():
    """Retorna o valor agregado total para cada estado."""
    args = valor_agregado_geral_args.parse_args(strict=True)

    db = SQLAlchemy.get_instance()

    entries = (
        db.session.query(
            UFModel.id.label("uf_id"),
            db.func.sum(ExportacaoModel.valor_agregado).label("valor_agregado_total")
        )
        .join(ExportacaoModel)
        .filter(ExportacaoModel.ano == args["ano"])
         .group_by(UFModel.id)
        .order_by(db.desc("valor_agregado_total"))
        .all()
    )

    return entries

    # comando p/ testes CMD
    # curl -X POST http://127.0.0.1:5000/api/exportacoes/valor-agregado/por-estado -H "Content-Type: application/json" -d "{\"ano\": 2023}"
