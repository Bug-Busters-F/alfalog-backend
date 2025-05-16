import pandas as pd
from ..ncms.model import NCMModel
from ..utils.sqlalchemy import SQLAlchemy
from . import BATCH_SIZE, LIMIT

baseurl = "https://balanca.economia.gov.br/balanca/bd/tabelas/NCM.csv"


def importar(replace: bool = False):
    """Importa dados de NCM do COMEX para o banco de dados."""
    exp_df_base = pd.read_csv(baseurl, sep=";", encoding="latin1")

    db = SQLAlchemy.get_instance()

    # Para cada linha do CSV, criar um objeto NCMModel e salvar no BD
    for index, row in exp_df_base.iterrows():

        ncm = db.session.query(NCMModel).filter_by(codigo=row["CO_NCM"]).first()
        if ncm and not replace:
            continue
        elif not ncm:
            ncm = NCMModel()

        ncm.codigo = str(row["CO_NCM"]).strip()
        ncm.descricao = str(row["NO_NCM_POR"]).strip()

        db.session.add(ncm)

        # Commit in batches
        if index % BATCH_SIZE == 0:
            db.session.commit()
        if index == LIMIT:
            break

    # Efetua o commit após inserir todos os registros
    db.session.commit()


if __name__ == "__main__":
    importar()
