import pandas as pd
from ..sh6s.model import SH6Model
from ..utils.sqlalchemy import SQLAlchemy
from . import BATCH_SIZE, LIMIT

baseurl = "https://balanca.economia.gov.br/balanca/bd/tabelas/NCM_SH.csv"


def importar(replace: bool = False):
    """Importa dados de SH6 e SH6 do COMEX para o banco de dados (ambos no mesmo CSV)."""
    df = pd.read_csv(baseurl, sep=";", encoding="latin1")
    db = SQLAlchemy.get_instance()

    # Loop para cada linha do CSV
    for index, row in df.iterrows():

        sh6 = db.session.query(SH6Model).filter_by(codigo=row["CO_SH6"]).first()
        if sh6 and not replace:
            continue
        elif not sh6:
            sh6 = SH6Model()

        sh6.codigo = str(row["CO_SH6"]).strip()
        sh6.nome = str(row["NO_SH6_POR"]).strip()

        db.session.add(sh6)

        # Commit in batches
        if index % BATCH_SIZE == 0:
            db.session.commit()
        if index == LIMIT:
            break

    db.session.commit()


if __name__ == "__main__":
    importar()
