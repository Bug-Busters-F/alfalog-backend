"""Format the data."""

from flask_restful import fields
from src.transacoes.fields import model_fields as transacao_fields

valor_agregado_fields = transacao_fields["data"]

cargas_movimentadas_fields = {
    "id": fields.Integer,
    "peso": fields.Integer,
    # FKs
    "ncm_id": fields.Integer,
}
