import pandas as pd
from ..ues.model import UEModel
from ..utils.sqlalchemy import SQLAlchemy

baseurl = "https://balanca.economia.gov.br/balanca/bd/tabelas/UE.csv"


def importar():
    """Importa dados de Unidades Estatísticas do COMEX para o banco de dados."""
    exp_df_base = pd.read_csv(baseurl, sep=";", encoding="latin1")

    db = SQLAlchemy.get_instance()

    for index, row in exp_df_base.iterrows():
        if index == 0:
            continue

        ue = UEModel()
        ue.codigo = row["CO_UNID"]  # Código da unidade estatística
        ue.nome = row["NO_NCM"]  # Nome completo da unidade
        ue.abreviacao = row["NO_NCM_ING"]  # Nome em inglês (usado como abreviação)

        db.session.add(ue)

    db.session.commit()


if __name__ == "__main__":
    importar()
