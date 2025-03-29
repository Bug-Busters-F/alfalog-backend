import pandas as pd
from ..ues.model import UEModel
from ..utils.sqlalchemy import SQLAlchemy
from . import BATCH_SIZE

baseurl = "https://balanca.economia.gov.br/balanca/bd/tabelas/NCM_UNIDADE.csv"


def importar(replace: bool = False):
    """Importa dados de Unidades Estatísticas do COMEX para o banco de dados."""
    exp_df_base = pd.read_csv(baseurl, sep=";", encoding="latin1")
    db = SQLAlchemy.get_instance()

    for index, row in exp_df_base.iterrows():
        if index == 0:
            continue

        ue = db.session.query(UEModel).filter_by(codigo=row["CO_UNID"]).first()
        if ue and not replace:
            continue
        elif not ue:
            ue = UEModel()

        ue.codigo = str(row["CO_UNID"]).strip()
        ue.nome = str(row["NO_UNID"]).strip()
        ue.abreviacao = str(row["SG_UNID"]).strip()

        db.session.add(ue)

        # Commit in batches
        if index % BATCH_SIZE == 0:
            db.session.commit()

    db.session.commit()


if __name__ == "__main__":
    importar()
