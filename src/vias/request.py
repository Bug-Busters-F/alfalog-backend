"""Validate input data."""

from flask_restful import reqparse

model_args = reqparse.RequestParser()
model_args.add_argument(
    "nome",
    type=str,
    required=True,
    help="Um nome deve ser informado.",
)
model_args.add_argument(
    "codigo",
    type=str,
    required=True,
    help="Um código deve ser informado.",
)
