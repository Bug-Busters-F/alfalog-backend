import pandas as pd
from ..urfs.model import URFModel
from ..utils.sqlalchemy import SQLAlchemy

baseurl = "https://balanca.economia.gov.br/balanca/bd/tabelas/URF.csv"


def importar():
    """Importa dados de URFs do COMEX para o banco de dados."""
    exp_df_base = pd.read_csv(baseurl, sep=";", encoding="latin1")

    db = SQLAlchemy.get_instance()

    # Para cada linha do CSV, criar um objeto URFModel e salvar no BD
    for index, row in exp_df_base.iterrows():
        # Se a primeira linha do CSV for cabeçalho, você pode pular index == 0
        if index == 0:
            continue

        urf = URFModel()
        urf.codigo = row["CO_URF"]  # Campo 'codigo' no Model
        urf.nome = row["NO_URF"]  # Campo 'nome' no Model

        db.session.add(urf)

    # Efetua o commit após inserir todos os registros
    db.session.commit()


if __name__ == "__main__":
    importar()
