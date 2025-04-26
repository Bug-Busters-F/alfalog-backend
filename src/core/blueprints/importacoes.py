import marshal
from flask import Blueprint, request
from flask_restful import marshal_with
from sqlalchemy import func
from ..request import valor_agregado_args, cargas_movimentadas_args
from ..fields import valor_agregado_fields, cargas_movimentadas_fields
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


    page = args["page"] or 1
    per_page = args["per_page"] or 20

    page = max(1, page)
    per_page = max(1, per_page)
    offset = (page - 1) * per_page

    db = SQLAlchemy.get_instance()

    total = (
        db.session.query(func.count(ImportacaoModel.id))
        .join(UFModel)
        .filter(UFModel.id == args["uf_id"], ImportacaoModel.ano == args["ano"])
        .scalar()
    )

    entries = (
        db.session.query(ImportacaoModel)
        .join(UFModel)
        .filter(UFModel.id == args["uf_id"], ImportacaoModel.ano == args["ano"])
        .order_by(ImportacaoModel.valor_agregado.desc())
        .limit(per_page)
        .offset(offset)
        .all()
    )

    response = {
        "total": total,
        "page": page,
        "per_page": per_page,
        "items": entries, 
    }


    return response


@importacoes.route("/api/importacoes/cargas-movimentadas", methods=["POST"])
@marshal_with(cargas_movimentadas_fields)
def cargas_movimentadas():
    """Inclui dados referente as cargas movimentadas."""
    # input validation
    args = cargas_movimentadas_args.parse_args(strict=True)

    page = args["page"] or 1
    per_page = args["per_page"] or 20

    page = max(1, page)
    per_page = max(1, per_page)
    offset = (page - 1) * per_page

    db = SQLAlchemy.get_instance()

    total = (
        db.session.query(func.count(ImportacaoModel.id))
        .join(UFModel)
        .filter(UFModel.id == args["uf_id"], ImportacaoModel.ano == args["ano"])
        .scalar()
    )

    entries = (
        db.session.query(
            ImportacaoModel.id,
            ImportacaoModel.peso,
            ImportacaoModel.ncm_id,
        )
        .join(UFModel)
        .filter(UFModel.id == args["uf_id"], ImportacaoModel.ano == args["ano"])
        .order_by(db.desc(ImportacaoModel.peso))
        .limit(per_page)
        .offset(offset)
        .all()
    )

    response = {
        "total": total,
        "page": page,
        "per_page": per_page,
        "cargas": entries, 
    }

    return response

