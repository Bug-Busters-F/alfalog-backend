from flask import Blueprint, request
from flask_restful import marshal_with, fields
from sqlalchemy import func, cast, Integer
from ..fields import balanca_comercial_fields
from ..request import balanca_comercial_args
from src.importacoes.model import ImportacaoModel
from src.somas.model import SomaModel
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

estatisticas_response_fields = {
    "numero_total_importacoes": fields.Integer,
    "numero_total_exportacoes": fields.Integer,
    "valor_agregado_total_importacao_reais": fields.String,
    "valor_agregado_total_exportacao_reais": fields.String
}

@main.route("/api/estatisticas-comerciais", methods=["GET"])
@marshal_with(estatisticas_response_fields)
def estatisticas_comerciais():
    nome_estado = request.args.get("estado", type=str)
    ano_inicio = request.args.get("ano_inicio", type=int)
    ano_fim = request.args.get("ano_fim", type=int)

    if not nome_estado or ano_inicio is None or ano_fim is None:
        return {"message": "Parâmetros 'estado', 'ano_inicio' e 'ano_fim' são obrigatórios."}, 400

    db = SQLAlchemy.get_instance()

    resultados = db.session.query(
        SomaModel.numero_total_importacoes,
        SomaModel.numero_total_exportacao,
        SomaModel.valor_agregado_total_importacao_reais,
        SomaModel.valor_agregado_total_exportacao_reais
    ).filter(
        func.lower(func.trim(SomaModel.estado)) == nome_estado.strip().lower(),
        cast(SomaModel.ano, Integer).between(ano_inicio, ano_fim)
    ).all()

    if not resultados:
        return {
            "numero_total_importacoes": 0,
            "numero_total_exportacoes": 0,
            "valor_agregado_total_importacao_reais": "0",
            "valor_agregado_total_exportacao_reais": "0"
        }

    total_imp = sum(r.numero_total_importacoes for r in resultados)
    total_exp = sum(r.numero_total_exportacao for r in resultados)
    valor_imp = sum(float(r.valor_agregado_total_importacao_reais) for r in resultados)
    valor_exp = sum(float(r.valor_agregado_total_exportacao_reais) for r in resultados)

    return {
        "numero_total_importacoes": total_imp,
        "numero_total_exportacoes": total_exp,
        "valor_agregado_total_importacao_reais": str(int(valor_imp)),
        "valor_agregado_total_exportacao_reais": str(int(valor_exp))
    }