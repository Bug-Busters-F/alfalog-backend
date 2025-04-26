import marshal
from flask import Blueprint, request
from flask_restful import marshal_with, marshal
from sqlalchemy import func, text
from ..request import valor_agregado_args, cargas_movimentadas_args, vias_utilizadas_args, urf_utilizadas_args
from ..fields import cargas_movimentadas_fields, valor_agregado_fields, vias_fields, urfs_fields
from src.exportacoes.model import ExportacaoModel
from src.ncms.model import NCMModel
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

    base_query = (
        db.session.query(
            ExportacaoModel.id,
            ExportacaoModel.ano,
            ExportacaoModel.mes,
            ExportacaoModel.peso,
            ExportacaoModel.valor,
            (ExportacaoModel.valor / func.nullif(ExportacaoModel.peso, 0)).label(
                "valor_agregado"
            ),  # Run on MySQL. Best for large datasets.
            ExportacaoModel.ncm_id,
            ExportacaoModel.ue_id,
            ExportacaoModel.pais_id,
            ExportacaoModel.uf_id,
            ExportacaoModel.via_id,
            ExportacaoModel.urf_id,
            NCMModel.descricao.label("ncm_descricao"),
        )
        .join(UFModel)
        .join(NCMModel)
        .filter(UFModel.id == args["uf_id"])
    )

    # filtering
    ano_inicial = args["ano_inicial"] if "ano_inicial" in args else None
    base_query = _filter_year_or_period(
        base_query,
        args["ano"],
        ano_inicial,
    )

    entries = base_query.order_by(text("valor_agregado DESC")).all()

    return entries


@exportacoes.route("/api/exportacoes/cargas-movimentadas", methods=["POST"])
@marshal_with(cargas_movimentadas_fields)
def cargas_movimentadas():
    """Inclui dados referente as cargas movimentadas."""
    # input validation
    args = cargas_movimentadas_args.parse_args(strict=True)

    db = SQLAlchemy.get_instance()

    base_query = (
        db.session.query(
            ExportacaoModel.id,
            ExportacaoModel.ano,
            ExportacaoModel.mes,
            ExportacaoModel.peso,
            ExportacaoModel.ncm_id,
            ExportacaoModel.uf_id,
            NCMModel.descricao.label("ncm_descricao"),
        )
        .join(UFModel)
        .join(NCMModel)
        .filter(UFModel.id == args["uf_id"])
    )

    # filtering
    ano_inicial = args["ano_inicial"] if "ano_inicial" in args else None
    base_query = _filter_year_or_period(
        base_query,
        args["ano"],
        ano_inicial,
    )

    entries = base_query.order_by(db.desc(ExportacaoModel.peso)).all()

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


@exportacoes.route("/api/exportacoes/urfs-utilizadas", methods=["POST"])
@marshal_with(urfs_fields)
def urfs_utilizadas():
    """Retorna as URFs e a quantidade de vezes que foram usadas."""
    args = urf_utilizadas_args.parse_args(strict=True)

    db = SQLAlchemy.get_instance()

    entries = (
        db.session.query(
            ExportacaoModel.urf_id.label("urf_id"),
            db.func.count(ExportacaoModel.urf_id).label("qtd")
        )
        .filter(ExportacaoModel.ano == args["ano"],ExportacaoModel.uf_id == args["uf_id"])
        .group_by(ExportacaoModel.urf_id)
        .all()
    )

    return entries

    # comando p/ testes CMD
    # curl -X POST http://127.0.0.1:5000/api/exportacoes/urfs-utilizadas -H "Content-Type: application/json" -d "{\"ano\": 2023, \"uf_id\": 12}"

@exportacoes.route("/api/exportacoes/download", methods=["GET"])
def download_exportacoes():
    """Download the original CSV file."""
    import os
    from flask import send_file, abort, current_app

    base_dir = os.path.dirname(current_app.root_path)
    csv_path = os.path.join(base_dir, "data", "dados_comex_EXP_2014_2024.csv")

    if not os.path.exists(csv_path):
        abort(404, description="File not found.")

    return send_file(
        csv_path,
        mimetype="text/csv",
        as_attachment=True,
        download_name="exportacoes.csv",
    )


def _filter_year_or_period(query, year_end: int, year_start: int = None):
    """Add year or period filtering to a query."""
    if year_start:
        return query.filter(ExportacaoModel.ano.between(year_start, year_end))
    return query.filter(ExportacaoModel.ano == year_end)
