"""Format the data."""

from flask_restful import fields


# Modelo de retorno ajustado para a paginação.
model_fields = {
    "data": {
    "total": fields.Integer,
    "page": fields.Integer,
    "per_page": fields.Integer,
    "items": fields.List(fields.Nested({
        "id": fields.Integer,
        "ano": fields.Integer,
        "mes": fields.Integer,
        "peso": fields.Integer,
        "valor": fields.Integer,
        "valor_agregado": fields.Float,
        "ncm_id": fields.Integer,
        "ue_id": fields.Integer,
        "pais_id": fields.Integer,
        "uf_id": fields.Integer,
        "via_id": fields.Integer,
        "urf_id": fields.Integer,
        "codigo": fields.String,
        "nome": fields.String,
    }))
}}


