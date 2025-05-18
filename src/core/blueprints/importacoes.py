import marshal
from flask import Blueprint, request
from flask_restful import marshal_with
from sqlalchemy import desc, func, text
from ..request import valor_agregado_args, cargas_movimentadas_args, vias_utilizadas_args, urf_utilizadas_args
from ..fields import response_fields_cargas_movimentadas, response_fields_valores_agregados, vias_fields, urfs_fields
from src.importacoes.model import ImportacaoModel
from src.ufs.model import UFModel
from src.ncms.model import NCMModel
from src.vias.model import ViaModel
from src.utils.sqlalchemy import SQLAlchemy


importacoes = Blueprint("importacoes", __name__)


@importacoes.route("/api/importacoes/valor-agregado", methods=["POST"])
@marshal_with(response_fields_valores_agregados)
def valor_agregado():
    """Retrieve Transações de Importação incluindo seu valor agregado, com paginação otimizada."""
    args = valor_agregado_args.parse_args(strict=True)
    db = SQLAlchemy.get_instance()

    tamanho_pagina = max(1, args["tamanho_pagina"])
    cursor = max(1, args["cursor"])
    offset = (cursor - 1) * tamanho_pagina

    valor_agregado_expr = (ImportacaoModel.valor / func.nullif(ImportacaoModel.peso, 0)).label("valor_agregado")

    base_query = (
        db.session.query(
            ImportacaoModel.id,
            ImportacaoModel.ano,
            ImportacaoModel.mes,
            ImportacaoModel.peso,
            ImportacaoModel.valor,
            valor_agregado_expr, 
            ImportacaoModel.ncm_id,
            ImportacaoModel.ue_id,
            ImportacaoModel.pais_id,
            ImportacaoModel.uf_id,
            ImportacaoModel.via_id,
            ImportacaoModel.urf_id,
            NCMModel.descricao.label("ncm_descricao"),
        )
        .select_from(ImportacaoModel)
        .join(UFModel, UFModel.id == ImportacaoModel.uf_id)
        .join(NCMModel, NCMModel.id == ImportacaoModel.ncm_id)
        .filter(UFModel.id == args["uf_id"])
    )

    ano_inicial = args.get("ano_inicial")
    base_query = _filter_year_or_period(base_query, args.get("ano"), ano_inicial)

    order_clause = (desc(valor_agregado_expr), desc(ImportacaoModel.id))

    # Buscar 'per_page + 1' registros
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

    # Montar a resposta estruturada
    response = {
        "pagina": cursor,
        "quantidade_pagina": tamanho_pagina,
        "has_next": has_next,
        "has_previous": has_previous,
        "valores_agregados": entries_paginadas,
    }

    return response


@importacoes.route("/api/importacoes/cargas-movimentadas", methods=["POST"])
@marshal_with(response_fields_cargas_movimentadas)
def cargas_movimentadas():
    """Inclui dados referente as cargas movimentadas."""
    # input validation
    args = cargas_movimentadas_args.parse_args(strict=True)

    # Cálculo da paginação
    tamanho_pagina = max(1, args["tamanho_pagina"])
    cursor = max(1, args["cursor"])
    offset = (cursor - 1) * tamanho_pagina
    valor_agregado_expr = (ImportacaoModel.valor / func.nullif(ImportacaoModel.peso, 0)).label("valor_agregado")

    db = SQLAlchemy.get_instance()

    base_query = (
        db.session.query(
            ImportacaoModel.id,
            ImportacaoModel.ano,
            ImportacaoModel.mes,
            ImportacaoModel.peso,
            ImportacaoModel.ncm_id,
            ImportacaoModel.uf_id,
            valor_agregado_expr,
            ImportacaoModel.pais_id,
            ImportacaoModel.via_id,
            NCMModel.descricao.label("ncm_descricao"),
        )
        .select_from(ImportacaoModel)
        .join(UFModel, UFModel.id == ImportacaoModel.uf_id)
        .join(NCMModel, NCMModel.id == ImportacaoModel.ncm_id)
        .filter(UFModel.id == args["uf_id"])
    )

    # filtering
    ano_inicial = args.get("ano_inicial") # Usar .get() para evitar KeyError se não existir
    base_query = _filter_year_or_period(base_query, args.get("ano"), ano_inicial)
    order_clause = (desc(ImportacaoModel.peso), desc(ImportacaoModel.id))

    num_to_fetch = tamanho_pagina + 1
    entries_plus_one = base_query.order_by(
        *order_clause
    ).limit(num_to_fetch).offset(offset).all()

    has_next = len(entries_plus_one) > tamanho_pagina

    # Obter apenas os registros da página atual
    entries_paginadas = entries_plus_one[:tamanho_pagina]

    has_previous = cursor > 1
    
    response = {
        "pagina": cursor,
        "quantidade_pagina": tamanho_pagina,
        "has_next": has_next,
        "has_previous": has_previous,
        "cargas_movimentadas": entries_paginadas,
    }

    return response


@importacoes.route("/api/importacoes/vias-utilizadas", methods=["POST"])
@marshal_with(vias_fields)
def vias_utilizadas():
    """Retorna as vias e a quantidade de vezes que foram usadas em um estado."""
    args = vias_utilizadas_args.parse_args(strict=True)

    db = SQLAlchemy.get_instance()
    # Condição do periodo
    filters = [ ImportacaoModel.uf_id == args["uf_id"] ]
    ano_inicial = args.get("periodo_ano_inicial")
    ano_final = args["periodo_ano_final"]
    if ano_inicial is not None:
        # Se o ano inicial for fornecido, filtramos no período [ano_inicial, ano_final]
        filters.append(ImportacaoModel.ano.between(ano_inicial, ano_final))
    else:
        # Se o ano inicial não for fornecido, filtramos apenas pelo ano final
        filters.append(ImportacaoModel.ano == ano_final)


    entries = (
        db.session.query(
            db.func.count(ImportacaoModel.via_id).label("qtd"),
            ImportacaoModel.via_id.label("via_id")
        )
        .join(ViaModel, ImportacaoModel.via_id == ViaModel.id)
        .filter(*filters)
        .group_by(ImportacaoModel.via_id)
        .all()
    )

    return entries

    # comando p/ testes CMD
    # curl -X POST http://127.0.0.1:5000/api/importacoes/vias-utilizadas -H "Content-Type: application/json" -d "{\"ano\": 2023, \"uf_id\": 12}"

@importacoes.route("/api/importacoes/urfs-utilizadas", methods=["POST"])
@marshal_with(urfs_fields)
def urfs_utilizadas():
    """Retorna as URFs e a quantidade de vezes que foram usadas."""
    args = urf_utilizadas_args.parse_args(strict=True)

    db = SQLAlchemy.get_instance()
    # Condição do periodo
    filters = [ ImportacaoModel.uf_id == args["uf_id"] ]
    ano_inicial = args.get("periodo_ano_inicial")
    ano_final = args["periodo_ano_final"]
    if ano_inicial is not None:
        # Se o ano inicial for fornecido, filtramos no período [ano_inicial, ano_final]
        filters.append(ImportacaoModel.ano.between(ano_inicial, ano_final))
    else:
        # Se o ano inicial não for fornecido, filtramos apenas pelo ano final
        filters.append(ImportacaoModel.ano == ano_final)

    entries = (
        db.session.query(
            ImportacaoModel.urf_id.label("urf_id"),
            db.func.count(ImportacaoModel.urf_id).label("qtd")
        )
        .filter(*filters)
        .group_by(ImportacaoModel.urf_id)
        .all()
    )

    return entries

    # comando p/ testes CMD
    # curl -X POST http://127.0.0.1:5000/api/exportacoes/urfs-utilizadas -H "Content-Type: application/json" -d "{\"ano\": 2023, \"uf_id\": 12}"


@importacoes.route("/api/importacoes/download", methods=["GET"])
def download_exportacoes():
    """Download the original CSV file."""
    import os
    from flask import send_file, abort, current_app

    base_dir = os.path.dirname(current_app.root_path)
    csv_path = os.path.join(base_dir, "data", "dados_comex_IMP_2014_2024.csv")

    if not os.path.exists(csv_path):
        abort(404, description="File not found.")

    return send_file(
        csv_path,
        mimetype="text/csv",
        as_attachment=True,
        download_name="importacoes.csv",
    )


def _filter_year_or_period(query, year_end: int, year_start: int = None):
    """Add year or period filtering to a query."""
    if year_start:
        return query.filter(ImportacaoModel.ano.between(year_start, year_end))
    return query.filter(ImportacaoModel.ano == year_end)

