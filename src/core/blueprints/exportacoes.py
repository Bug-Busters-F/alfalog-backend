import marshal
import time
from flask import Blueprint, request, jsonify
from flask_restful import marshal_with, marshal
from sqlalchemy import func
from ..request import valor_agregado_args, cargas_movimentadas_args
from ..fields import cargas_movimentadas_fields, valor_agregado_fields
from src.exportacoes.model import ExportacaoModel
from src.ufs.model import UFModel
from src.utils.sqlalchemy import SQLAlchemy


exportacoes = Blueprint("exportacoes", __name__)


@exportacoes.route("/api/exportacoes/valor-agregado", methods=["POST"])
@marshal_with(valor_agregado_fields)
def valor_agregado():
    start_time = time.time()

    args = valor_agregado_args.parse_args(strict=True)
    db = SQLAlchemy.get_instance()

    page = args["page"] or 1
    per_page = args["per_page"] or 20

    page = max(1, page)
    per_page = max(1, per_page)
    offset = (page - 1) * per_page

    # Fazendo a pre contagem dos dados antes de forma mais rapida
    total = (
        db.session.query(func.count(ExportacaoModel.id))
        .join(UFModel)
        .filter(UFModel.id == args["uf_id"], ExportacaoModel.ano == args["ano"])
        .scalar()
    )

    # Pegando os itens conforme o necessario
    items = (
        db.session.query(ExportacaoModel)
        .join(UFModel)
        .filter(UFModel.id == args["uf_id"], ExportacaoModel.ano == args["ano"])
        .order_by(ExportacaoModel.valor_agregado.desc())
        .limit(per_page)
        .offset(offset)
        .all()
    )

    response = {
        "total": total,
        "page": page,
        "per_page": per_page,
        "items": items, 
    }

    elapsed_time = time.time() - start_time
    print(f"Tempo da requisição: {elapsed_time:.4f} segundos")

    return response



@exportacoes.route("/api/exportacoes/cargas-movimentadas", methods=["POST"])
@marshal_with(cargas_movimentadas_fields)
def cargas_movimentadas():
    db = SQLAlchemy.get_instance()
    """Inclui dados referente as cargas movimentadas."""
    # input validation
    args = cargas_movimentadas_args.parse_args(strict=True)

    # Sessão para paginação
    page = args["page"] or 1
    per_page = args["per_page"] or 20

    page = max(1, page)
    per_page = max(1, per_page)
    offset = (page - 1) * per_page

    entries = (
        db.session.query(
            ExportacaoModel.id,
            ExportacaoModel.peso,
            ExportacaoModel.ncm_id,
        )
        .join(UFModel)
        .filter(UFModel.id == args["uf_id"], ExportacaoModel.ano == args["ano"])
        .order_by(db.desc(ExportacaoModel.peso))
        .limit(per_page)
        .offset(offset)
        .all()
    )

    total = (
        db.session.query(func.count(ExportacaoModel.id))
        .join(UFModel)
        .filter(UFModel.id == args["uf_id"], ExportacaoModel.ano == args["ano"])
        .scalar()
    )


    response = {
        "total": total,
        "page": page,
        "per_page": per_page,
        "cargas": entries, 
    }

    return response
