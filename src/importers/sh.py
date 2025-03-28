import pandas as pd
from ..sh4s.model import SH4Model
from ..sh6s.model import SH6Model
from ..utils.sqlalchemy import SQLAlchemy

baseurl = "https://balanca.economia.gov.br/balanca/bd/tabelas/NCM_SH.csv"


def importar():
    """Importa dados de SH4 e SH6 do COMEX para o banco de dados (ambos no mesmo CSV)."""
    df = pd.read_csv(baseurl, sep=";", encoding="latin1")
    db = SQLAlchemy.get_instance()

    # Loop para cada linha do CSV
    for index, row in df.iterrows():
        # Se a primeira linha do CSV for cabeçalho, podemos pular index == 0
        if index == 0:
            continue

        # Cria e popula o objeto SH4Model
        sh4 = SH4Model()
        sh4.codigo = row["CO_SH4"]  # coluna que representa o código de 4 dígitos
        sh4.nome = row["NO_SH4_POR"]  # coluna que representa o nome em português

        # Cria e popula o objeto SH6Model
        sh6 = SH6Model()
        sh6.codigo = row["CO_SH6"]  # coluna que representa o código de 6 dígitos
        sh6.nome = row["NO_SH6_POR"]  # coluna que representa o nome em português

        # Adiciona ambos os objetos ao banco
        db.session.add(sh4)
        db.session.add(sh6)

    # Efetiva a gravação de todos os registros no final
    db.session.commit()


if __name__ == "__main__":
    importar()
