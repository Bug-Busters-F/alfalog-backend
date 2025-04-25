import marshal
from flask import Blueprint, request
from flask_restful import marshal_with
from ..request import balanca_comercial_args
from ..fields import balanca_comercial_fields
from src.importacoes.model import ImportacaoModel
from src.exportacoes.model import ExportacaoModel
from src.ufs.model import UFModel
from src.utils.sqlalchemy import SQLAlchemy
from sqlalchemy import func

main = Blueprint("main", __name__)


@main.route("/api/balanca-comercial", methods=["POST"])
@marshal_with(balanca_comercial_fields)
def calcular_balanca_comercial():
    """Calcula a balança comercial (exportação - importação) por ano para um estado."""
    # validação da entrada
    args = balanca_comercial_args.parse_args(strict=True)

    db = SQLAlchemy.get_instance()

    uf_id = args["uf_id"]

    # Buscar somatório de importações
    importacoes = (
        db.session.query(
            ImportacaoModel.ano,
            func.sum(ImportacaoModel.valor).label("total_importado")
        )
        .filter(ImportacaoModel.uf_id == uf_id)
        .group_by(ImportacaoModel.ano)
        .all()
    )

    # Buscar somatório de exportações
    exportacoes = (
        db.session.query(
            ExportacaoModel.ano,
            func.sum(ExportacaoModel.valor).label("total_exportado")
        )
        .filter(ExportacaoModel.uf_id == uf_id)
        .group_by(ExportacaoModel.ano)
        .all()
    )

    # Transformar em dicionário {ano: valor}
    dict_importacoes = {i.ano: i.total_importado for i in importacoes}
    dict_exportacoes = {e.ano: e.total_exportado for e in exportacoes}

    # Unir todos os anos
    anos = sorted(set(dict_importacoes.keys()).union(dict_exportacoes.keys()))

    resultado = []
    for ano in anos:
        valor_exportado = dict_exportacoes.get(ano, 0)
        valor_importado = dict_importacoes.get(ano, 0)
        balanca = valor_exportado - valor_importado

        resultado.append({
            "ano": ano,
            "valor": balanca
        })

    return resultado