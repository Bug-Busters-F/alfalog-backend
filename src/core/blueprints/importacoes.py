import marshal
from flask import Blueprint, request
from flask_restful import marshal_with
from ..request import valor_agregado_args, cargas_movimentadas_args, vias_utilizadas_args, urf_utilizadas_args
from ..fields import valor_agregado_fields, cargas_movimentadas_fields, vias_fields, urfs_fields
from src.importacoes.model import ImportacaoModel
from src.ufs.model import UFModel
from src.vias.model import ViaModel
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

@importacoes.route("/api/importacoes/vias-utilizadas", methods=["POST"])
@marshal_with(vias_fields)
def vias_utilizadas():
    """Retorna as vias e a quantidade de vezes que foram usadas em um estado."""
    args = vias_utilizadas_args.parse_args(strict=True)

    db = SQLAlchemy.get_instance()

    entries = (
        db.session.query(
            db.func.count(ImportacaoModel.via_id).label("qtd"),
            ImportacaoModel.via_id.label("via_id")
        )
        .join(ViaModel, ImportacaoModel.via_id == ViaModel.id)
        .filter(ImportacaoModel.ano == args["ano"], ImportacaoModel.uf_id == args["uf_id"])
        .group_by(ImportacaoModel.via_id)
        .all()
    )

    return entries

    # comando p/ testes CMD
    # curl -X POST http://127.0.0.1:5000/api/importacoes/vias-utilizadas -H "Content-Type: application/json" -d "{\"ano\": 2023, \"uf_id\": 12}"

@importacoes.route("/api/importacoes/urfs-utilizadas", methods=["POST"])
@marshal_with(urfs_fields)
def urfs_utilizadas():
    """Retorna as URFs e a quantidade de vezes que foram usadas."""
    args = urf_utilizadas_args.parse_args(strict=True)

    db = SQLAlchemy.get_instance()

    entries = (
        db.session.query(
            ImportacaoModel.urf_id.label("urf_id"),
            db.func.count(ImportacaoModel.urf_id).label("qtd")
        )
        .filter(
            ImportacaoModel.ano == args["ano"],
            ImportacaoModel.uf_id == args["uf_id"]
        )
        .group_by(ImportacaoModel.urf_id)
        .all()
    )

    return entries

    # comando p/ testes CMD
    # curl -X POST http://127.0.0.1:5000/api/exportacoes/urfs-utilizadas -H "Content-Type: application/json" -d "{\"ano\": 2023, \"uf_id\": 12}"