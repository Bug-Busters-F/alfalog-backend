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
valor_agregado_args.add_argument(
    "page",
    type=int,
    required=False,
    default=1,
)
valor_agregado_args.add_argument(
    "per_page",
    type=int,
    required=False,
    default=10,
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
