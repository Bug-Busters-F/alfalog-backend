import pandas as pd
from ..sh4s.model import SH4Model
from ..utils.sqlalchemy import SQLAlchemy
from . import BATCH_SIZE, LIMIT

baseurl = "https://balanca.economia.gov.br/balanca/bd/tabelas/NCM_SH.csv"


def importar(replace: bool = False):
    """Importa dados de SH4 e SH6 do COMEX para o banco de dados (ambos no mesmo CSV)."""
    df = pd.read_csv(baseurl, sep=";", encoding="latin1")
    db = SQLAlchemy.get_instance()

    # Loop para cada linha do CSV
    for index, row in df.iterrows():

        sh4 = db.session.query(SH4Model).filter_by(codigo=row["CO_SH4"]).first()
        if sh4 and not replace:
            continue
        elif not sh4:
            sh4 = SH4Model()

        sh4.codigo = str(row["CO_SH4"]).strip()
        sh4.nome = str(row["NO_SH4_POR"]).strip()

        db.session.add(sh4)

        # Commit in batches
        if index % BATCH_SIZE == 0:
            db.session.commit()
        if index == LIMIT:
            break

    db.session.commit()


if __name__ == "__main__":
    importar()
