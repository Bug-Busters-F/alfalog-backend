import pandas as pd
from ..paises.model import PaisModel
from ..utils.sqlalchemy import SQLAlchemy

baseurl = "https://balanca.economia.gov.br/balanca/bd/tabelas/PAIS.csv"


def importar():
    """Importa dados de Paises do COMEX para o banco de dados."""
    exp_df_base = pd.read_csv(baseurl, sep=";", encoding="latin1")

    db = SQLAlchemy.get_instance()

    # para cada linha do CSV, criar um objeto PaisModel e salvar no BD
    for index, row in exp_df_base.iterrows():
        # Se a primeira linha do CSV for cabeçalho, você pode pular index == 0
        if index == 0:
            continue

        pais = PaisModel()
        pais.codigo = row["CO_PAIS"]
        pais.nome = row["NO_PAIS"]

        db.session.add(pais)
        db.session.commit()


if __name__ == "__main__":
    importar()
