from flask_restful import reqparse

model_args = reqparse.RequestParser()
model_args.add_argument("ano", type=int, required=True, help="Ano é obrigatório.")
model_args.add_argument("valor", type=int, required=True, help="Valor é obrigatório.")
model_args.add_argument("id_uf", type=int, required=True, help="ID da UF é obrigatório.")
