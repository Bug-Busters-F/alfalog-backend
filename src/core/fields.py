"""Format the data."""

from flask_restful import fields
from src.exportacoes.fields import model_fields as transacao_fields

valor_agregado_fields = transacao_fields["data"]


# Correção no retorno da requisição para suportar a paginação
cargas_movimentadas_fields = {
    "total": fields.Integer,
    "page": fields.Integer,
    "per_page": fields.Integer,
    "cargas": fields.List(fields.Nested({
        "id": fields.Integer,
        "peso": fields.Integer,
        "ncm_id": fields.Integer,
    }))
}


