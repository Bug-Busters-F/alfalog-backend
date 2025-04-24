from .transacoes import importar_dados


def importar(db, caminho_csv):
    importar_dados(db, caminho_csv, "importacoes")
