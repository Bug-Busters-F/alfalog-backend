"""Format the data."""

from flask_restful import fields


model_fields = {
    "data": {
        "id": fields.Integer,
        "codigo": fields.String,
        "nome": fields.String,
        "ano": fields.Integer,
        "mes": fields.Integer,
        "peso": fields.Integer,
        "valor": fields.Integer,
        "valor_agregado": fields.Float,
        # FKs
        "ncm_id": fields.Integer,
        "ue_id": fields.Integer,
        "pais_id": fields.Integer,
        "uf_id": fields.Integer,
        "via_id": fields.Integer,
        "urf_id": fields.Integer,
    },
}
