"""Format the data."""

from flask_restful import fields
from src.exportacoes.fields import model_fields as transacao_fields

valor_agregado_fields = transacao_fields["data"]

cargas_movimentadas_fields = {
    "id": fields.Integer,
    "peso": fields.Integer,
    # FKs
    "ncm_id": fields.Integer,
}

vias_fields = {
    "via_id": fields.Integer,
    "qtd": fields.Integer,
}

valor_agregado_por_estado_fields = {
    "uf_id": fields.Integer,
    "valor_agregado_total": fields.Integer,
}