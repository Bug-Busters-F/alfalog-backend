"""Validate input data."""

from flask_restful import reqparse


"""
    Argumentos para valor [ Carga Movimentadas, Valor Agregado ]
    uf_id:int          -  ID da sigla do uf informado
    ano:int            -  Ano que ocorreu
    ano_inicila:int    -  Ano inicial da busca que ocorreu a importação/exportação
    tamanho_pagina:int -  Quantidades de intes por pagina
    cursor:int         -  Pagina indicada
"""
# Valor Agregado
valor_agregado_args = reqparse.RequestParser()
valor_agregado_args.add_argument(
    "uf_id", type=int, required=True, help="ID da UF inválido."
)
valor_agregado_args.add_argument(
    "ano", type=int, required=True, help="Um ano deve ser informado."
)
valor_agregado_args.add_argument(
    "ano_inicial",
    type=int,
    required=False,
    help="Informe um ano de início para visualizar um período.",
)
valor_agregado_args.add_argument("tamanho_pagina", type=int, required=False, default=10)
valor_agregado_args.add_argument("cursor", type=int, required=False, default=0)
# Cargas Movimentadas
cargas_movimentadas_args = reqparse.RequestParser()
cargas_movimentadas_args.add_argument(
    "uf_id", type=int, required=True, help="ID da UF inválido."
)
cargas_movimentadas_args.add_argument(
    "ano", type=int, required=True, help="Um ano deve ser informado."
)
cargas_movimentadas_args.add_argument(
    "ano_inicial",
    type=int,
    required=False,
    help="Informe um ano de início para visualizar um período.",
)
cargas_movimentadas_args.add_argument(
    "tamanho_pagina", type=int, required=False, default=10
)
cargas_movimentadas_args.add_argument("cursor", type=int, required=False, default=0)

"""
    Argumentos para valor [ Vias utilizadas, URF Utilizadas ]
    uf_id:int          -  ID da sigla do uf informado
    ano:int            -  Ano que ocorreu
"""
# Vias utilizadas
vias_utilizadas_args = reqparse.RequestParser()
vias_utilizadas_args.add_argument(
    "ano", type=int, required=True, help="Um ano deve ser informado."
)
vias_utilizadas_args.add_argument(
    "uf_id", type=int, required=True, help="ID da UF inválido."
)
vias_utilizadas_args.add_argument(
    "ano_inicial",
    type=int,
    required=False,
    help="Informe um ano de início para visualizar um período.",
)
# Urf utilizadas
urf_utilizadas_args = reqparse.RequestParser()
urf_utilizadas_args.add_argument(
    "ano", type=int, required=True, help="Um ano deve ser informado."
)
urf_utilizadas_args.add_argument(
    "uf_id", type=int, required=True, help="ID da UF inválido."
)
urf_utilizadas_args.add_argument(
    "ano_inicial",
    type=int,
    required=False,
    help="Informe um ano de início para visualizar um período.",
)

"""
    Argumentos para valor [ Balança Comercial ]
    uf_id:int          -  ID da sigla do uf informado
"""
# Balança comercial
balanca_comercial_args = reqparse.RequestParser()
balanca_comercial_args.add_argument(
    "uf_id", type=int, required=True, help="UF ID obrigatório"
)
