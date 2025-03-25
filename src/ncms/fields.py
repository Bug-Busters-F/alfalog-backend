"""Format the data."""

from flask_restful import fields


model_fields = {
    "data": {
        "id": fields.Integer,
        "codigo": fields.String,
        "descricao": fields.String,
    },
}
