from flask import Blueprint, request
from flask_restful import marshal_with, fields
from sqlalchemy import func
from ..fields import balanca_comercial_fields
from ..request import balanca_comercial_args
from src.importacoes.model import ImportacaoModel
from src.exportacoes.model import ExportacaoModel
from src.utils.sqlalchemy import SQLAlchemy
from src.ncms.model import NCMModel

main = Blueprint("main", __name__)


balanca_comercial_response_fields = {
    "balanca": fields.List(fields.Nested(balanca_comercial_fields))
}

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