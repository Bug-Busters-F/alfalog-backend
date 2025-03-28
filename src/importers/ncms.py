import pandas as pd
from ..ncms.model import NCMModel
from ..utils.sqlalchemy import SQLAlchemy

baseurl = "https://balanca.economia.gov.br/balanca/bd/tabelas/NCM.csv"


def importar():
    """Importa dados de NCM do COMEX para o banco de dados."""
    exp_df_base = pd.read_csv(baseurl, sep=";", encoding="latin1")

    db = SQLAlchemy.get_instance()

    # Para cada linha do CSV, criar um objeto NCMModel e salvar no BD
    for index, row in exp_df_base.iterrows():
        # Se a primeira linha do CSV for cabeçalho, podemos pular index == 0
        if index == 0:
            continue

        ncm = NCMModel()
        ncm.codigo = row["CO_NCM"]  # Campo 'codigo' no Model
        ncm.descricao = row["NO_NCM"]  # Campo 'descricao' no Model

        db.session.add(ncm)

    # Efetua o commit após inserir todos os registros
    db.session.commit()


if __name__ == "__main__":
    importar()
