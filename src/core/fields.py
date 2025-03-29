"""Format the data."""

from flask_restful import fields

valor_agregado_fields = {
    "id": fields.Integer,
    "valor_agregado": fields.Float,  #
    "codigo": fields.String,
    "nome": fields.String,
    "ano": fields.Integer,
    "mes": fields.Integer,
    "quantidade": fields.Integer,
    "peso": fields.Integer,
    "valor": fields.Integer,
    # FKs
    "ncm_id": fields.Integer,
    "ue_id": fields.Integer,
    "pais_id": fields.Integer,
    "uf_id": fields.Integer,
    "via_id": fields.Integer,
    "urf_id": fields.Integer,
}
