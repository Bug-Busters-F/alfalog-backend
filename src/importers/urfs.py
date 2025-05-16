import pandas as pd
from ..urfs.model import URFModel
from ..utils.sqlalchemy import SQLAlchemy
from . import BATCH_SIZE, LIMIT

baseurl = "https://balanca.economia.gov.br/balanca/bd/tabelas/URF.csv"


def importar(replace: bool = False):
    """Importa dados de URFs do COMEX para o banco de dados."""
    exp_df_base = pd.read_csv(baseurl, sep=";", encoding="latin1")

    db = SQLAlchemy.get_instance()

    # Para cada linha do CSV, criar um objeto URFModel e salvar no BD
    for index, row in exp_df_base.iterrows():

        urf = db.session.query(URFModel).filter_by(codigo=row["CO_URF"]).first()
        if urf and not replace:
            continue
        elif not urf:
            urf = URFModel()

        urf.codigo = str(row["CO_URF"]).strip()
        urf.nome = str(row["NO_URF"]).strip()

        db.session.add(urf)

        # Commit in batches
        if index % BATCH_SIZE == 0:
            db.session.commit()
        if index == LIMIT:
            break

    db.session.commit()


if __name__ == "__main__":
    importar()
