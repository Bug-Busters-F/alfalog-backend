"""Validate input data."""

from flask_restful import reqparse

model_args = reqparse.RequestParser()
model_args.add_argument(
    "id",
    type=int,
    help="O ID é opcional e não será utilizado.",
)
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
model_args.add_argument(
    "abreviacao",
    type=str,
    required=True,
    help="Uma abreviação deve ser informada.",
)
