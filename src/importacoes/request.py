"""Validate input data."""

from flask_restful import reqparse

model_args = reqparse.RequestParser()
model_args.add_argument(
    "id",
    type=int,
    help="O ID é opcional e não será utilizado.",
)
model_args.add_argument(
    "ano",
    type=int,
    required=True,
    help="Um ano deve ser informado.",
)
model_args.add_argument(
    "mes",
    type=int,
    required=True,
    help="Um mês deve ser informado.",
)
model_args.add_argument(
    "peso",
    type=int,
    required=True,
    help="Um peso deve ser informado.",
)
model_args.add_argument(
    "valor",
    type=int,
    required=True,
    help="Um valor deve ser informado.",
)

# FKs
model_args.add_argument(
    "ncm_id",
    type=int,
    help="Um ID de NCM deve ser informado.",
)
model_args.add_argument(
    "ue_id",
    type=int,
    help="Um ID de Unidade Estatística (UE) deve ser informado.",
)
model_args.add_argument(
    "pais_id",
    type=int,
    help="Um ID de País deve ser informado.",
)
model_args.add_argument(
    "uf_id",
    type=int,
    help="Um ID de Unidade Federativa (UF) deve ser informado.",
)
model_args.add_argument(
    "via_id",
    type=int,
    help="Um ID de Via de transporte deve ser informado.",
)
model_args.add_argument(
    "urf_id",
    type=int,
    help="Um ID de Unidade da Receita Federal (URF) deve ser informado.",
)
