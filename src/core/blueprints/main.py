from flask import Blueprint, request
from flask_restful import marshal_with, fields
from sqlalchemy import func
from ..fields import balanca_comercial_fields
from ..request import balanca_comercial_args
from src.importacoes.model import ImportacaoModel
from src.exportacoes.model import ExportacaoModel
from src.utils.sqlalchemy import SQLAlchemy

main = Blueprint("main", __name__)


balanca_comercial_response_fields = {
    "balanca": fields.List(fields.Nested(balanca_comercial_fields))
}

@main.route("/api/balanca-comercial", methods=["POST"])
@marshal_with(balanca_comercial_response_fields)
def calcular_balanca_comercial():
    """Calcula a balança comercial (exportação - importação) por ano para um estado."""
    args = balanca_comercial_args.parse_args(strict=True)
    db = SQLAlchemy.get_instance()

    uf_id = args["uf_id"]

    # Importações por ano
    importacoes = db.session.query(
        ImportacaoModel.ano,
        func.sum(ImportacaoModel.valor).label("total")
    ).filter(
        ImportacaoModel.uf_id == uf_id
    ).group_by(
        ImportacaoModel.ano
    ).all()

    # Exportações por ano
    exportacoes = db.session.query(
        ExportacaoModel.ano,
        func.sum(ExportacaoModel.valor).label("total")
    ).filter(
        ExportacaoModel.uf_id == uf_id
    ).group_by(
        ExportacaoModel.ano
    ).all()

    # Transformar em dicionário 
    dict_importacoes = {i.ano: i.total for i in importacoes}
    dict_exportacoes = {e.ano: e.total for e in exportacoes}

   
    anos = sorted(set(dict_importacoes.keys()) | set(dict_exportacoes.keys()))

    resultado = []
    for ano in anos:
        total_exportado = dict_exportacoes.get(ano, 0) or 0
        total_importado = dict_importacoes.get(ano, 0) or 0
        balanca = total_exportado - total_importado

        resultado.append({
            "ano": ano,
            "valor": balanca
        })

    return {"balanca": resultado}
