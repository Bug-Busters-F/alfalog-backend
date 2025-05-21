from flask import Blueprint, request
from flask_restful import marshal_with, fields
from sqlalchemy import func
from src.core.fields import balanca_variacao_fields
from sqlalchemy import func, cast, Integer
from ..fields import balanca_comercial_fields
from ..request import balanca_comercial_args
from src.importacoes.model import ImportacaoModel
from src.somas.model import SomaModel
from src.exportacoes.model import ExportacaoModel
from src.balanca.model import BalancaModel
from src.utils.sqlalchemy import SQLAlchemy
from src.ncms.model import NCMModel

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
    args = balanca_comercial_args.parse_args(strict=True)
    db = SQLAlchemy.get_instance()

    uf_id = args["uf_id"]

    importacoes = db.session.query(
        ImportacaoModel.ano,
        func.sum(ImportacaoModel.valor).label("total")
    ).filter(
        ImportacaoModel.uf_id == uf_id
    ).group_by(
        ImportacaoModel.ano
    ).all()

    exportacoes = db.session.query(
        ExportacaoModel.ano,
        func.sum(ExportacaoModel.valor).label("total")
    ).filter(
        ExportacaoModel.uf_id == uf_id
    ).group_by(
        ExportacaoModel.ano
    ).all()

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

# Rota CardSomas
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

@main.route("/api/balanca-comercial/ncm", methods=["POST"])
def balanca_comercial_por_ncm():
    db = SQLAlchemy.get_instance()
    data = request.get_json()

    ncm_codigo = data.get("ncm")

    if not ncm_codigo:
        return {"error": "ncm é obrigatório"}, 400

    filters_imp = [NCMModel.codigo == ncm_codigo]
    filters_exp = [NCMModel.codigo == ncm_codigo]

    importacoes = (
        db.session.query(
            ImportacaoModel.ano,
            func.sum(ImportacaoModel.valor).label("total_importado")
        )
        .join(ImportacaoModel.ncm)
        .filter(*filters_imp)
        .group_by(ImportacaoModel.ano)
        .order_by(ImportacaoModel.ano)
        .all()
    )

    exportacoes = (
        db.session.query(
            ExportacaoModel.ano,
            func.sum(ExportacaoModel.valor).label("total_exportado")
        )
        .join(ExportacaoModel.ncm)
        .filter(*filters_exp)
        .group_by(ExportacaoModel.ano)
        .order_by(ExportacaoModel.ano)
        .all()
    )

    imp_dict = {i.ano: i.total_importado for i in importacoes}
    exp_dict = {e.ano: e.total_exportado for e in exportacoes}

    anos = sorted(set(imp_dict.keys()) | set(exp_dict.keys()))

    resultado = []
    for ano in anos:
        importado = imp_dict.get(ano, 0)
        exportado = exp_dict.get(ano, 0)
        saldo = exportado - importado

        resultado.append({
            "year": ano,
            "value": saldo
        })

    return {"dados": resultado}
