import pandas as pd
from ..ufs.model import UFModel
from ..utils.sqlalchemy import SQLAlchemy

baseurl = "https://balanca.economia.gov.br/balanca/bd/tabelas/UF.csv"


def importar():
    """Importa dados de UFs do COMEX para o banco de dados."""
    exp_df_base = pd.read_csv(baseurl, sep=";", encoding="latin1")

    db = SQLAlchemy.get_instance()

    # para cada linha,
    #    criar um objeto com os dados
    #    salvar no bd

    # para cada linha
    for index, row in exp_df_base.iterrows():
        if index == 0:
            continue
        uf = UFModel()
        uf.codigo = row["CO_UF"]
        uf.nome = row["NO_UF"]
        uf.sigla = row["SG_UF"]
        uf.nome_regiao = row["NO_REGIAO"]
        db.session.add(uf)
        db.session.commit()


if __main__ == "__name__":
    importar()
