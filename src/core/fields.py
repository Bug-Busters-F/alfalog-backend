"""Format the data."""

from flask_restful import fields
from src.exportacoes.fields import model_fields as transacao_fields

# valor_agregado_fields = transacao_fields["data"]
# valor_agregado_fields["ncm_descricao"] = fields.String
valor_agregado_fields = {
    "id": fields.Integer,
    "ano": fields.Integer,
    "mes": fields.Integer,
    "peso": fields.Integer,
    "valor": fields.Integer,
    "valor_agregado": fields.Float,
    # FKs
    "ncm_descricao": fields.String,
    "ncm_id": fields.Integer,
    "ue_id": fields.Integer,
    "pais_id": fields.Integer,
    "uf_id": fields.Integer,
    "via_id": fields.Integer,
    "urf_id": fields.Integer,
}
cargas_movimentadas_fields = {
    "id": fields.Integer,
    "ano": fields.Integer,
    "mes": fields.Integer,
    "peso": fields.Integer,
    # FKs
    "ncm_id": fields.Integer,
    "ncm_descricao": fields.String,
    "uf_id": fields.Integer,
}

vias_fields = {
    "via_id": fields.Integer,
    "qtd": fields.Integer,
}

urfs_fields = {
    "urf_id": fields.Integer,
    "qtd": fields.Integer,
}

balanca_comercial_fields = {
    "ano": fields.Integer,
    "valor": fields.Float,
}
