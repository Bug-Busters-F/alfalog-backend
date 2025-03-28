import pandas as pd

BASE_URL = "https://balanca.economia.gov.br/balanca/bd/comexstat-bd/ncm/"
YEARS = range(2014, 2025)
TIPO = "EXP"
OUTPUT_FINAL = f"{TIPO}_2014-2023_FULL.csv"


def aplicar_filtros(df):
    df = df[df["CO_UNID"] != 18].copy()
    df = df[~df["CO_PAIS"].isin([0, 990, 994, 995, 997, 998, 999])].copy()
    df = df[~df["SG_UF_NCM"].isin(["ND", "ZN", "ED", "RE", "MN", "CB", "EX"])].copy()
    df = df[~df["CO_VIA"].isin([0, 3, 8, 10, 12, 13, 14, 99])].copy()
    df = df[~df["CO_URF"].isin([0, 815400, 1010109, 8110000, 9999999])].copy()
    df = df[df["QT_ESTAT"] != 0].copy()
    df = df[df["KG_LIQUIDO"] != 0].copy()
    df = df[df["VL_FOB"] != 0].copy()
    return df


def processar_arquivos():
    dfs_filtrados = []

    for year in YEARS:
        try:
            url = f"{BASE_URL}{TIPO}_{year}.csv"
            print(f"Processando {TIPO} {year}...")

            df = pd.read_csv(url, sep=";", encoding="latin1")
            df_filtrado = aplicar_filtros(df)
            dfs_filtrados.append(df_filtrado)

            print(f"Concluído: {year} ({len(df_filtrado)} registros)")
        except Exception as e:
            print(f"Erro ao processar {year}: {str(e)}")

    if dfs_filtrados:
        df_consolidado = pd.concat(dfs_filtrados, ignore_index=True)

        df_consolidado.to_csv(OUTPUT_FINAL, sep=";", index=False, encoding="latin1")
        print(f"\nArquivo de todos os anos salvo como: {OUTPUT_FINAL}")
        print(f"Total de registros: {len(df_consolidado)}")
    else:
        print("Nenhum arquivo foi processado com sucesso.")


# if __name__ == "__main__": ###Testar
#     processar_arquivos()
