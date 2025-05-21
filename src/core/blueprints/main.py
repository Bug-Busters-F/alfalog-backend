from flask import Blueprint, request
from flask_restful import marshal_with, fields
from sqlalchemy import func
from src.core.fields import balanca_variacao_fields
from ..fields import balanca_comercial_fields
from ..request import balanca_comercial_args
from src.importacoes.model import ImportacaoModel
from src.exportacoes.model import ExportacaoModel
from src.balanca.model import BalancaModel
from src.utils.sqlalchemy import SQLAlchemy

main = Blueprint("main", __name__)


balanca_comercial_response_fields = {
    "balanca": fields.List(fields.Nested(balanca_comercial_fields))
}

balanca_comercial_variacao_response_fields = {
    "balanca": fields.List(fields.Nested(balanca_variacao_fields))
}

def calcular_variacao_percentual(valor_inicial, valor_final):
    if valor_inicial == 0:
        if valor_final == 0:
            return 0
        return 100 if valor_final > 0 else -100
    return round(((valor_final - valor_inicial) / abs(valor_inicial)) * 100, 2)

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

@main.route("/api/top-estados-ascencao-declinio", methods=["POST"])
@marshal_with(balanca_comercial_variacao_response_fields)
def top_estados_ascencao_declinio():
    """Retorna os top 5 estados em ascensão e top 5 estados em declínio de acordo com a variação percentual entre dois anos."""

    args = request.get_json()

    ano_inicial = args.get("ano_inicial")
    ano_final = args.get("ano_final")

    db = SQLAlchemy.get_instance()

    balancas = db.session.query(
        BalancaModel.uf_id,
        BalancaModel.ano,
        BalancaModel.valor
    ).filter(
        BalancaModel.ano.in_(range(ano_inicial, ano_final + 1))
    ).all()

    dados_balanca = {(b.uf_id, b.ano): b.valor for b in balancas}

    estados_variacao = []

    for uf_id in set([b.uf_id for b in balancas]):
        valores = [dados_balanca.get((uf_id, ano), 0) for ano in range(ano_inicial, ano_final + 1)]
        valor_inicial = valores[0]
        valor_final = valores[-1]

        percentual_variacao = calcular_variacao_percentual(valor_inicial, valor_final)

        estados_variacao.append({
            "uf_id": uf_id,
            "percentual_variacao": percentual_variacao,
            "valores": valores
        })

    estados_ascensao = sorted(estados_variacao, key=lambda x: x["percentual_variacao"], reverse=True)[:5]
    estados_declinio = sorted(estados_variacao, key=lambda x: x["percentual_variacao"])[:5]

    return {"balanca": estados_ascensao + estados_declinio}