"""Format the data."""

from flask_restful import fields
from src.exportacoes.fields import model_fields as transacao_fields

# valor_agregado_fields = transacao_fields["data"]
# valor_agregado_fields["ncm_descricao"] = fields.String

# Campos adicionados para paginação onde eles se referem as quantidades para dados do front-end para
# fazer a paginação de forma pratica e eficiente
# total - total de itens que existe dentro da busca total
valor_agregado_fields = {
    "id": fields.Integer,
    "ano": fields.Integer,
    "mes": fields.Integer,
    "peso": fields.Integer,
    "valor": fields.Integer,
    "valor_agregado": fields.Float,
    "ncm_descricao": fields.String,
    "ncm_id": fields.Integer,
    "ue_id": fields.Integer,
    "pais_id": fields.Integer,
    "uf_id": fields.Integer,
    "via_id": fields.Integer,
    "urf_id": fields.Integer,
}

response_fields_valores_agregados = {
    "pagina": fields.Integer,
    "quantidade_pagina": fields.Integer,
    "has_next": fields.Boolean,
    "has_previous": fields.Boolean,
    "valores_agregados": fields.List(fields.Nested(valor_agregado_fields)),
}


cargas_movimentadas_fields = {
    "id": fields.Integer,
    "ano": fields.Integer,
    "mes": fields.Integer,
    "peso": fields.Integer,
    "valor_agregado": fields.Float,
    # FKs
    "via_id": fields.Integer,
    "pais_id": fields.Integer,
    "ncm_id": fields.Integer,
    "ncm_descricao": fields.String,
    "uf_id": fields.Integer,
}

response_fields_cargas_movimentadas = {
    "pagina": fields.Integer,
    "quantidade_pagina": fields.Integer,
    "has_next": fields.Boolean,
    "has_previous": fields.Boolean,
    "cargas_movimentadas": fields.List(fields.Nested(cargas_movimentadas_fields)),
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

balanca_variacao_fields = {
    "uf_id": fields.Integer,
    "percentual_variacao": fields.Float,
    "valores": fields.List(fields.Integer),
}

forecast_fields = {
    "id": fields.Integer,
    "ds": fields.String,
    "y": fields.Float,
    "yhat": fields.Float,
    "yhat_lower": fields.Float,
    "yhat_upper": fields.Float,
    "trend": fields.Float,
    "trend_lower": fields.Float,
    "trend_upper": fields.Float,
    "additive_terms": fields.Float,
    "additive_terms_lower": fields.Float,
    "additive_terms_upper": fields.Float,
    "yearly": fields.Float,
    "yearly_lower": fields.Float,
    "yearly_upper": fields.Float,
    "multiplicative_terms": fields.Float,
    "multiplicative_terms_lower": fields.Float,
    "multiplicative_terms_upper": fields.Float,
}
