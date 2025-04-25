"""Validate input data."""

from flask_restful import reqparse

valor_agregado_args = reqparse.RequestParser()
valor_agregado_args.add_argument(
    "uf_id",
    type=int,
    required=True,
    help="ID da UF inválido.",
)
valor_agregado_args.add_argument(
    "ano",
    type=int,
    required=True,
    help="Um ano deve ser informado.",
)

cargas_movimentadas_args = reqparse.RequestParser()
cargas_movimentadas_args.add_argument(
    "uf_id",
    type=int,
    required=True,
    help="ID da UF inválido.",
)
cargas_movimentadas_args.add_argument(
    "ano",
    type=int,
    required=True,
    help="Um ano deve ser informado.",
)

vias_utilizadas_args = reqparse.RequestParser()
vias_utilizadas_args.add_argument(
    "ano",
    type=int,
    required=True,
    help="Um ano deve ser informado.",
)
vias_utilizadas_args.add_argument(
    "uf_id",
    type=int,
    required=True,
    help="ID da UF inválido.",
)

valor_agregado_geral_args = reqparse.RequestParser()
valor_agregado_geral_args.add_argument(
    "ano",
    type=int,
    required=True,
    help="Um ano deve ser informado.",
)