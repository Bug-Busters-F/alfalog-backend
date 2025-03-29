import pandas as pd
from ..paises.model import PaisModel
from ..utils.sqlalchemy import SQLAlchemy
from . import BATCH_SIZE

baseurl = "https://balanca.economia.gov.br/balanca/bd/tabelas/PAIS.csv"


def importar(replace: bool = False):
    """Importa dados de Paises do COMEX para o banco de dados."""
    exp_df_base = pd.read_csv(baseurl, sep=";", encoding="latin1")

    db = SQLAlchemy.get_instance()

    # para cada linha do CSV, criar um objeto PaisModel e salvar no BD
    for index, row in exp_df_base.iterrows():
        # Se a primeira linha do CSV for cabeçalho, você pode pular index == 0
        if index == 0:
            continue

        pais = db.session.query(PaisModel).filter_by(codigo=row["CO_PAIS"]).first()
        if pais and not replace:
            continue
        elif not pais:
            pais = PaisModel()

        pais.codigo = str(row["CO_PAIS"]).strip()
        pais.nome = str(row["NO_PAIS"]).strip()

        db.session.add(pais)

        # Commit in batches
        if index % BATCH_SIZE == 0:
            db.session.commit()

    db.session.commit()


if __name__ == "__main__":
    importar()
