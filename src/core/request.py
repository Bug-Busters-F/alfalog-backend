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
