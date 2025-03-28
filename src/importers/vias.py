import pandas as pd
from ..vias.model import ViaModel
from ..utils.sqlalchemy import SQLAlchemy

baseurl = "https://balanca.economia.gov.br/balanca/bd/tabelas/VIA.csv"


def importar():
    """Importa dados de Vias do COMEX para o banco de dados."""
    exp_df_base = pd.read_csv(baseurl, sep=";", encoding="latin1")

    db = SQLAlchemy.get_instance()

    # para cada linha do CSV, criar um objeto ViaModel e salvar no BD
    for index, row in exp_df_base.iterrows():
        # Se a primeira linha do CSV for cabeçalho, você pode pular index == 0
        if index == 0:
            continue

        via = ViaModel()
        via.codigo = row["CO_VIA"]  # corresponde ao campo 'codigo' no Model
        via.nome = row["NO_VIA"]  # corresponde ao campo 'nome' no Model

        db.session.add(via)
        db.session.commit()


if __name__ == "__main__":
    importar()
