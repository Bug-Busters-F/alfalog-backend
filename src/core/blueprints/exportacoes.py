import marshal
from flask import Blueprint, request
from flask_restful import marshal_with, marshal
from sqlalchemy import desc, func, text
from ..request import valor_agregado_args, cargas_movimentadas_args, vias_utilizadas_args, urf_utilizadas_args
from ..fields import response_fields_cargas_movimentadas, response_fields_valores_agregados, vias_fields, urfs_fields
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
    db = SQLAlchemy.get_instance() # Ou sua forma de obter a instância do DB

    # Cálculo da paginação
    tamanho_pagina = max(1, args["tamanho_pagina"])
    cursor = max(1, args["cursor"])
    offset = (cursor - 1) * tamanho_pagina

    valor_agregado_expr = (ExportacaoModel.valor / func.nullif(ExportacaoModel.peso, 0)).label("valor_agregado")

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

    ano_inicial = args.get("ano_inicial") # Usar .get() para evitar KeyError se não existir
    base_query = _filter_year_or_period(base_query, args["ano"], ano_inicial)

    order_clause = (desc(valor_agregado_expr), desc(ExportacaoModel.id))

    # Buscar 'tamanho_pagina + 1' registros para checar se há próxima página
    num_to_fetch = tamanho_pagina + 1
    entries_plus_one = base_query.order_by(
        *order_clause
    ).limit(num_to_fetch).offset(offset).all()

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

    valor_agregado_expr = (ExportacaoModel.valor / func.nullif(ExportacaoModel.peso, 0)).label("valor_agregado")


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

    ano_inicial = args.get("ano_inicial") # Usar .get() para evitar KeyError se não existir
    base_query = _filter_year_or_period(base_query, args.get("ano"), ano_inicial)
    order_clause = (desc(ExportacaoModel.peso), desc(ExportacaoModel.id))

    # Buscar 'tamanho_pagina + 1' registros
    num_to_fetch = tamanho_pagina + 1
    entries_plus_one = base_query.order_by(
        *order_clause
    ).limit(num_to_fetch).offset(offset).all()

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

    # Condição do periodo
    filters = [ ExportacaoModel.uf_id == args["uf_id"] ]
    ano_inicial = args.get("periodo_ano_inicial")
    ano_final = args["periodo_ano_final"]

    if ano_inicial is not None:
        # Se o ano inicial for fornecido, filtramos no período [ano_inicial, ano_final]
        filters.append(ExportacaoModel.ano.between(ano_inicial, ano_final))
    else:
        # Se o ano inicial não for fornecido, filtramos apenas pelo ano final
        filters.append(ExportacaoModel.ano == ano_final)

    base_query = (
        db.session.query(
            func.count(ExportacaoModel.via_id).label("qtd"),
            ExportacaoModel.via_id.label("via_id")
        )
        .select_from(ExportacaoModel)
        .join(ViaModel, ExportacaoModel.via_id == ViaModel.id)
        .filter(*filters)
        .group_by(ExportacaoModel.via_id)
        .order_by(desc("qtd"))
    )

    entries = base_query.all()
    return entries
    # comando p/ testes CMD
    # curl -X POST http://127.0.0.1:5000/api/exportacoes/vias-utilizadas -H "Content-Type: application/json" -d "{\"ano\": 2023, \"uf_id\": 12}"


@exportacoes.route("/api/exportacoes/urfs-utilizadas", methods=["POST"])
@marshal_with(urfs_fields)
def urfs_utilizadas():
    """Retorna as URFs e a quantidade de vezes que foram usadas."""
    args = urf_utilizadas_args.parse_args(strict=True)

    db = SQLAlchemy.get_instance()
    
    # Condição do periodo
    filters = [ ExportacaoModel.uf_id == args["uf_id"] ]
    ano_inicial = args.get("periodo_ano_inicial")
    ano_final = args["periodo_ano_final"]
    
    if ano_inicial is not None:
        # Se o ano inicial for fornecido, filtramos no período [ano_inicial, ano_final]
        filters.append(ExportacaoModel.ano.between(ano_inicial, ano_final))
    else:
        # Se o ano inicial não for fornecido, filtramos apenas pelo ano final
        filters.append(ExportacaoModel.ano == ano_final)

    entries = (
        db.session.query(
            ExportacaoModel.urf_id.label("urf_id"),
            db.func.count(ExportacaoModel.urf_id).label("qtd")
        )
        .filter(*filters)
        .group_by(ExportacaoModel.urf_id)
        .all()
    )

    return entries

    # comando p/ testes CMD
    # curl -X POST http://127.0.0.1:5000/api/exportacoes/urfs-utilizadas -H "Content-Type: application/json" -d "{\"ano\": 2023, \"uf_id\": 12}"

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
