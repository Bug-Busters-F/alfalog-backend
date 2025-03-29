import pandas as pd
from ..ufs.model import UFModel
from ..utils.sqlalchemy import SQLAlchemy
from . import BATCH_SIZE, LIMIT

baseurl = "https://balanca.economia.gov.br/balanca/bd/tabelas/UF.csv"


def importar(replace: bool = False):
    """Importa dados de UFs do COMEX para o banco de dados."""
    exp_df_base = pd.read_csv(baseurl, sep=";", encoding="latin1")

    db = SQLAlchemy.get_instance()

    # para cada linha
    for index, row in exp_df_base.iterrows():
        if index == 0:
            continue

        uf = db.session.query(UFModel).filter_by(codigo=row["CO_UF"]).first()
        if uf and not replace:
            continue
        elif not uf:
            uf = UFModel()

        uf.codigo = str(row["CO_UF"]).strip()
        uf.nome = str(row["NO_UF"]).strip()
        uf.sigla = str(row["SG_UF"]).strip()
        uf.nome_regiao = str(row["NO_REGIAO"]).strip()

        db.session.add(uf)

        # Commit in batches
        if index % BATCH_SIZE == 0:
            db.session.commit()
        if index == LIMIT:
            break

    db.session.commit()


if __name__ == "__main__":
    importar()
