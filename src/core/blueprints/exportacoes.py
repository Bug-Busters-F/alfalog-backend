import marshal
from flask import Blueprint, request
from flask_restful import marshal_with, marshal
from sqlalchemy import desc, func, text
from ..request import (
    valor_agregado_args,
    cargas_movimentadas_args,
    vias_utilizadas_args,
    urf_utilizadas_args,
)
from ..fields import (
    response_fields_cargas_movimentadas,
    response_fields_valores_agregados,
    vias_fields,
    urfs_fields,
)
from src.exportacoes.model import ExportacaoModel
from src.ncms.model import NCMModel
from src.ufs.model import UFModel
from src.vias.model import ViaModel
from src.utils.sqlalchemy import SQLAlchemy


exportacoes = Blueprint("exportacoes", __name__)


@exportacoes.route("/api/exportacoes/valor-agregado", methods=["POST"])
@marshal_with(response_fields_valores_agregados)
def valor_agregado():
    args = valor_agregado_args.parse_args(strict=True)
    db = SQLAlchemy.get_instance()  # Ou sua forma de obter a instância do DB

    # Cálculo da paginação
    tamanho_pagina = max(1, args["tamanho_pagina"])
    cursor = max(1, args["cursor"])
    offset = (cursor - 1) * tamanho_pagina

    valor_agregado_expr = (
        ExportacaoModel.valor / func.nullif(ExportacaoModel.peso, 0)
    ).label("valor_agregado")

    base_query = (
        db.session.query(
            ExportacaoModel.id,
            ExportacaoModel.ano,
            ExportacaoModel.mes,
            ExportacaoModel.peso,
            ExportacaoModel.valor,
            valor_agregado_expr,
            ExportacaoModel.ncm_id,
            ExportacaoModel.ue_id,
            ExportacaoModel.pais_id,
            ExportacaoModel.uf_id,
            ExportacaoModel.via_id,
            ExportacaoModel.urf_id,
            NCMModel.descricao.label("ncm_descricao"),
        )
        .select_from(ExportacaoModel)
        .join(UFModel, UFModel.id == ExportacaoModel.uf_id)
        .join(NCMModel, NCMModel.id == ExportacaoModel.ncm_id)
        .filter(UFModel.id == args["uf_id"])
    )

    ano_inicial = args.get(
        "ano_inicial"
    )  # Usar .get() para evitar KeyError se não existir
    base_query = _filter_year_or_period(base_query, args["ano"], ano_inicial)

    order_clause = (desc(valor_agregado_expr), desc(ExportacaoModel.id))

    # Buscar 'tamanho_pagina + 1' registros para checar se há próxima página
    num_to_fetch = tamanho_pagina + 1
    entries_plus_one = (
        base_query.order_by(*order_clause).limit(num_to_fetch).offset(offset).all()
    )

    # Determinar se existe uma próxima página
    # Se buscamos N+1 e recebemos N+1, então há mais registros -> has_next = True
    has_next = len(entries_plus_one) > tamanho_pagina

    # Obter apenas os registros da página atual (os N primeiros)
    # Se len(entries_plus_one) for N+1, pegamos os N primeiros.
    # Se for N ou menos, pegamos todos que vieram.
    entries_paginadas = entries_plus_one[:tamanho_pagina]

    # Determinar se existe página anterior (lógica simples baseada no cursor)
    has_previous = cursor > 1

    response = {
        "pagina": cursor,
        "quantidade_pagina": tamanho_pagina,
        "has_next": has_next,
        "has_previous": has_previous,
        "valores_agregados": entries_paginadas,
    }

    return response


@exportacoes.route("/api/exportacoes/cargas-movimentadas", methods=["POST"])
@marshal_with(response_fields_cargas_movimentadas)
def cargas_movimentadas():
    db = SQLAlchemy.get_instance()
    args = cargas_movimentadas_args.parse_args(strict=True)

    valor_agregado_expr = (
        ExportacaoModel.valor / func.nullif(ExportacaoModel.peso, 0)
    ).label("valor_agregado")

    # Cálculo da paginação
    tamanho_pagina = max(1, args["tamanho_pagina"])
    cursor = max(1, args["cursor"])
    offset = (cursor - 1) * tamanho_pagina

    # Query base
    base_query = (
        db.session.query(
            ExportacaoModel.id,
            ExportacaoModel.ano,
            ExportacaoModel.mes,
            ExportacaoModel.peso,
            ExportacaoModel.ncm_id,
            ExportacaoModel.uf_id,
            valor_agregado_expr,
            ExportacaoModel.pais_id,
            ExportacaoModel.via_id,
            NCMModel.descricao.label("ncm_descricao"),
        )
        .select_from(ExportacaoModel)
        .join(UFModel, UFModel.id == ExportacaoModel.uf_id)
        .join(NCMModel, NCMModel.id == ExportacaoModel.ncm_id)
        .filter(UFModel.id == args["uf_id"])
    )

    ano_inicial = args.get(
        "ano_inicial"
    )  # Usar .get() para evitar KeyError se não existir
    base_query = _filter_year_or_period(base_query, args.get("ano"), ano_inicial)
    order_clause = (desc(ExportacaoModel.peso), desc(ExportacaoModel.id))

    # Buscar 'tamanho_pagina + 1' registros
    num_to_fetch = tamanho_pagina + 1
    entries_plus_one = (
        base_query.order_by(*order_clause).limit(num_to_fetch).offset(offset).all()
    )

    # Determinar se há uma próxima página
    has_next = len(entries_plus_one) > tamanho_pagina

    # Obter apenas os registros da página atual
    entries_paginadas = entries_plus_one[:tamanho_pagina]

    # Determinar se há página anterior
    has_previous = cursor > 1

    response = {
        "pagina": cursor,
        "quantidade_pagina": tamanho_pagina,
        "has_next": has_next,
        "has_previous": has_previous,
        "cargas_movimentadas": entries_paginadas,
    }

    return response


@exportacoes.route("/api/exportacoes/vias-utilizadas", methods=["POST"])
@marshal_with(vias_fields)
def vias_utilizadas():
    """Retorna as vias e a quantidade de vezes que foram usadas em um estado e ano."""
    args = vias_utilizadas_args.parse_args(strict=True)
    db = SQLAlchemy.get_instance()

    # Condição do período
    filters = [ExportacaoModel.uf_id == args["uf_id"]]
    ano_inicial = args.get("ano_inicial")
    ano_final = args["ano_final"]

    if ano_inicial is not None:
        filters.append(ExportacaoModel.ano.between(ano_inicial, ano_final))
    else:
        filters.append(ExportacaoModel.ano == ano_final)

    base_query = (
        db.session.query(
            func.count(ExportacaoModel.via_id).label("qtd"),
            ExportacaoModel.via_id.label("via_id"),
        )
        .select_from(ExportacaoModel)
        .join(ViaModel, ExportacaoModel.via_id == ViaModel.id)
        .filter(*filters)
        .group_by(ExportacaoModel.via_id)
        .order_by(desc("qtd"))
    )

    entries = base_query.all()
    return entries


@exportacoes.route("/api/exportacoes/urfs-utilizadas", methods=["POST"])
@marshal_with(urfs_fields)
def urfs_utilizadas():
    """Retorna as URFs e a quantidade de vezes que foram usadas."""
    args = urf_utilizadas_args.parse_args(strict=True)
    db = SQLAlchemy.get_instance()

    # Filtros com base no período e UF
    filters = [ExportacaoModel.uf_id == args["uf_id"]]
    ano_inicial = args.get("ano_inicial")
    ano_final = args["ano_final"]

    if ano_inicial is not None:
        filters.append(ExportacaoModel.ano.between(ano_inicial, ano_final))
    else:
        filters.append(ExportacaoModel.ano == ano_final)

    base_query = (
        db.session.query(
            ExportacaoModel.urf_id.label("urf_id"),
            db.func.count(ExportacaoModel.urf_id).label("qtd"),
        )
        .filter(*filters)
        .group_by(ExportacaoModel.urf_id)
        .order_by(db.func.count(ExportacaoModel.urf_id).desc())
    )

    entries = base_query.all()
    return entries


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


@exportacoes.route("/api/exportacoes/comparacao-estados", methods=["POST"])
def estatisticas_por_estado_imp():
    """Retorna os dados de dois estados passados no parametro pelo uf_id"""
    db = SQLAlchemy.get_instance()
    args = request.get_json()

    estados = args.get("estados")
    ano_inicial = args.get("ano_inicial")
    ano_final = args.get("ano_final")

    if not estados or not ano_inicial or not ano_final:
        return {
            "message": "Parâmetros obrigatórios: estados, ano_inicial, ano_final"
        }, 400

    resultados = (
        db.session.query(
            ExportacaoModel.uf_id,
            ExportacaoModel.ano,
            func.sum(ExportacaoModel.valor).label("export_valor"),
            func.sum(ExportacaoModel.peso).label("peso"),
        )
        .filter(
            ExportacaoModel.uf_id.in_(estados),
            ExportacaoModel.ano.between(ano_inicial, ano_final),
        )
        .group_by(ExportacaoModel.uf_id, ExportacaoModel.ano)
        .order_by(ExportacaoModel.uf_id, ExportacaoModel.ano)
        .all()
    )

    retorno = []
    for row in resultados:
        retorno.append(
            {
                "state": row.uf_id,
                "year": row.ano,
                "Valor FOB": float(row.export_valor or 0),
                "Peso (Kg)": float(row.peso or 0),
            }
        )

    return retorno


@exportacoes.route("/api/exportacoes/graficos-pesquisa", methods=["POST"])
def graficos_pesquisa_exportacoes():
    db = SQLAlchemy.get_instance()
    data = request.get_json()

    ncm = data.get("ncm")
    ano_inicial = data.get("ano_inicial")
    ano_final = data.get("ano_final")

    filters = []
    if ncm:
        filters.append(NCMModel.codigo == ncm)
    if ano_inicial and ano_final:
        filters.append(ExportacaoModel.ano.between(ano_inicial, ano_final))

    # JOIN necessário se for filtrar por código NCM
    query_base = db.session.query(ExportacaoModel).join(ExportacaoModel.ncm)

    def get_result(group_by_field):
        return (
            query_base.filter(*filters)
            .with_entities(
                group_by_field, func.sum(ExportacaoModel.valor).label("total")
            )
            .group_by(group_by_field)
            .order_by(func.sum(ExportacaoModel.valor).desc())
            .limit(6)
            .all()
        )

    estados = get_result(ExportacaoModel.uf_id)
    vias = get_result(ExportacaoModel.via_id)
    urfs = get_result(ExportacaoModel.urf_id)
    paises = get_result(ExportacaoModel.pais_id)

    return {
        "por_estado": [{"uf_id": r[0], "total": r[1]} for r in estados],
        "por_via": [{"via_id": r[0], "total": r[1]} for r in vias],
        "por_urf": [{"urf_id": r[0], "total": r[1]} for r in urfs],
        "por_pais": [{"pais_id": r[0], "total": r[1]} for r in paises],
    }
