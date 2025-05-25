from flask_restful import fields

model_fields = {
    "id": fields.Integer,
    "ano": fields.Integer,
    "valor": fields.Integer,
    "id_uf": fields.Integer,
}
