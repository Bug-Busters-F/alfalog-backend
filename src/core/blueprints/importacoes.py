import marshal
from flask import Blueprint, request
from flask_restful import marshal_with
from sqlalchemy import func, text
from ..request import valor_agregado_args, cargas_movimentadas_args
from ..fields import valor_agregado_fields, cargas_movimentadas_fields
from src.importacoes.model import ImportacaoModel
from src.ufs.model import UFModel
from src.ncms.model import NCMModel
from src.utils.sqlalchemy import SQLAlchemy


importacoes = Blueprint("importacoes", __name__)


@importacoes.route("/api/importacoes/valor-agregado", methods=["POST"])
@marshal_with(valor_agregado_fields)
def valor_agregado():
    """Retrieve Transações incluindo seu valor agregado."""
    # input validation
    args = valor_agregado_args.parse_args(strict=True)

    db = SQLAlchemy.get_instance()

    base_query = (
        db.session.query(
            ImportacaoModel.id,
            ImportacaoModel.ano,
            ImportacaoModel.mes,
            ImportacaoModel.peso,
            ImportacaoModel.valor,
            (ImportacaoModel.valor / func.nullif(ImportacaoModel.peso, 0)).label(
                "valor_agregado"
            ),  # Run on MySQL. Best for large datasets.
            ImportacaoModel.ncm_id,
            ImportacaoModel.ue_id,
            ImportacaoModel.pais_id,
            ImportacaoModel.uf_id,
            ImportacaoModel.via_id,
            ImportacaoModel.urf_id,
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


@importacoes.route("/api/importacoes/cargas-movimentadas", methods=["POST"])
@marshal_with(cargas_movimentadas_fields)
def cargas_movimentadas():
    """Inclui dados referente as cargas movimentadas."""
    # input validation
    args = cargas_movimentadas_args.parse_args(strict=True)

    db = SQLAlchemy.get_instance()

    base_query = (
        db.session.query(
            ImportacaoModel.id,
            ImportacaoModel.ano,
            ImportacaoModel.mes,
            ImportacaoModel.peso,
            ImportacaoModel.ncm_id,
            ImportacaoModel.uf_id,
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

    entries = base_query.order_by(db.desc(ImportacaoModel.peso)).all()

    return entries


def _filter_year_or_period(query, year_end: int, year_start: int = None):
    """Add year or period filtering to a query."""
    if year_start:
        return query.filter(ImportacaoModel.ano.between(year_start, year_end))
    return query.filter(ImportacaoModel.ano == year_end)
