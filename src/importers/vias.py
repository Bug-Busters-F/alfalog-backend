import pandas as pd
from ..vias.model import ViaModel
from ..utils.sqlalchemy import SQLAlchemy
from . import BATCH_SIZE, LIMIT

baseurl = "https://balanca.economia.gov.br/balanca/bd/tabelas/VIA.csv"


def importar(replace: bool = False):
    """Importa dados de Vias do COMEX para o banco de dados."""
    exp_df_base = pd.read_csv(baseurl, sep=";", encoding="latin1")

    db = SQLAlchemy.get_instance()

    # para cada linha do CSV, criar um objeto ViaModel e salvar no BD
    for index, row in exp_df_base.iterrows():
        # Se a primeira linha do CSV for cabeçalho, você pode pular index == 0
        if index == 0:
            continue

        via = db.session.query(ViaModel).filter_by(codigo=row["CO_VIA"]).first()
        if via and not replace:
            continue
        elif not via:
            via = ViaModel()

        via.codigo = str(row["CO_VIA"]).strip()
        via.nome = str(row["NO_VIA"]).strip()

        db.session.add(via)

        # Commit in batches
        if index % BATCH_SIZE == 0:
            db.session.commit()
        if index == LIMIT:
            break

    db.session.commit()


if __name__ == "__main__":
    importar()
