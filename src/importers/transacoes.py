import pandas as pd
from tqdm import tqdm
from src import create_app
from src.utils.sqlalchemy import SQLAlchemy
from src.ufs.model import UFModel as UF
from src.ncms.model import NCMModel as NCM
from src.paises.model import PaisModel as Pais
from src.transacoes.model import TransacaoModel as Transacao
from src.vias.model import ViaModel as Via
from src.urfs.model import URFModel as URF
from src.ues.model import UEModel as UE
from . import LIMIT

BASE_URL = "https://balanca.economia.gov.br/balanca/bd/comexstat-bd/ncm/"
TIPO = "EXP"


class DataLoader:
    def __init__(self, db_instance):
        self.db = db_instance

    def aplicar_filtros(self, df):
        if "SG_UF_NCM" in df.columns and "CO_UF" not in df.columns:
            df = df.rename(columns={"SG_UF_NCM": "CO_UF"})

        df = df[df["CO_UNID"] != 18].copy()
        df = df[~df["CO_PAIS"].isin([0, 990, 994, 995, 997, 998, 999])].copy()
        df = df[~df["CO_UF"].isin(["ND", "ZN", "ED", "RE", "MN", "CB", "EX"])].copy()
        df = df[~df["CO_VIA"].isin([0, 8, 10, 11, 12, 13, 99])].copy()
        df = df[~df["CO_URF"].isin([0, 815400, 1010109, 8110000, 9999999])].copy()
        df = df[df["QT_ESTAT"] != 0].copy()
        df = df[df["VL_FOB"] != 0].copy()

        # Aplicar filtro IQR para remover outliers no KG_LIQUIDO
        Q1 = df["KG_LIQUIDO"].quantile(0.25)
        Q3 = df["KG_LIQUIDO"].quantile(0.75)
        IQR = Q3 - Q1

        # Definir limites para outliers
        lim_inferior = Q1 - 1.5 * IQR
        lim_superior = Q3 + 1.5 * IQR

        # Filtrar os dados
        df = df[(df["KG_LIQUIDO"] >= lim_inferior) & (df["KG_LIQUIDO"] <= lim_superior)].copy() 

        return df.head(LIMIT)

    def processar_arquivo_2024(self):
        try:
            url = f"{BASE_URL}{TIPO}_2024.csv"
            print(f"Processando {TIPO} 2024...")
            df = pd.read_csv(url, sep=";", encoding="latin1")
            df_filtrado = self.aplicar_filtros(df)
            print(f"Concluído: 2024 ({len(df_filtrado)} registros)")
            return df_filtrado
        except Exception as e:
            print(f"Erro ao processar arquivo de 2024: {str(e)}")
            return None

    def carregar_dados(self, df):
        if df is None or df.empty:
            print("Nenhum dado para carregar")
            return

        chunk_size = 100  # Tamanho do lote, se for um numero grande de registros aumente o chunk_size
        total_chunks = len(df) // chunk_size + (1 if len(df) % chunk_size != 0 else 0)

        for i in tqdm(range(total_chunks), desc="Carregando dados"):
            chunk = df.iloc[i * chunk_size : (i + 1) * chunk_size]

            transacoes = []
            relacionamentos = {
                "uf": {},
                "ncm": {},
                "pais": {},
                "via": {},
                "urf": {},
                "ue": {},
            }

            # processa todos os relacionamentos
            for _, row in chunk.iterrows():
                # UF
                sigla_uf = str(row["CO_UF"]).strip().upper()
                if sigla_uf not in relacionamentos["uf"]:
                    ue = self.db.session.query(UF).filter_by(sigla=sigla_uf).first()
                    if not ue:
                        ue = UF(
                            codigo=sigla_uf,
                            sigla=sigla_uf,
                            nome=f"Estado-{sigla_uf}",
                            nome_regiao=f"Região-{sigla_uf}",
                        )
                        self.db.session.add(ue)
                        self.db.session.flush()
                    relacionamentos["uf"][sigla_uf] = ue

                # NCM
                codigo_ncm = str(row["CO_NCM"])
                if codigo_ncm not in relacionamentos["ncm"]:
                    ncm = (
                        self.db.session.query(NCM).filter_by(codigo=codigo_ncm).first()
                    )
                    if not ncm:
                        ncm = NCM(codigo=codigo_ncm, descricao=f"NCM {codigo_ncm}")
                        self.db.session.add(ncm)
                        self.db.session.flush()
                    relacionamentos["ncm"][codigo_ncm] = ncm

                # País
                codigo_pais = int(row["CO_PAIS"])
                if codigo_pais not in relacionamentos["pais"]:
                    pais = (
                        self.db.session.query(Pais)
                        .filter_by(codigo=codigo_pais)
                        .first()
                    )
                    if not pais:
                        pais = Pais(codigo=codigo_pais, nome=f"País-{codigo_pais}")
                        self.db.session.add(pais)
                    relacionamentos["pais"][codigo_pais] = pais

                # Via
                codigo_via = int(row["CO_VIA"])
                if codigo_via not in relacionamentos["via"]:
                    via = (
                        self.db.session.query(Via).filter_by(codigo=codigo_via).first()
                    )
                    if not via:
                        via = Via(codigo=codigo_via, nome=f"Via-{codigo_via}")
                        self.db.session.add(via)
                    relacionamentos["via"][codigo_via] = via

                # URF
                codigo_urf = int(row["CO_URF"])
                if codigo_urf not in relacionamentos["urf"]:
                    urf = (
                        self.db.session.query(URF).filter_by(codigo=codigo_urf).first()
                    )
                    if not urf:
                        urf = URF(codigo=codigo_urf, nome=f"URF-{codigo_urf}")
                        self.db.session.add(urf)
                    relacionamentos["urf"][codigo_urf] = urf

                # UE
                codigo_ue = int(row["CO_UNID"])
                if codigo_ue not in relacionamentos["ue"]:
                    codigo_ue_str = str(codigo_ue)
                    ue = (
                        self.db.session.query(UE)
                        .filter_by(codigo=codigo_ue_str)
                        .first()
                    )
                    if not ue:
                        ue = UE(
                            codigo=codigo_ue_str,
                            nome=f"Unidade Estatística {codigo_ue}",
                            abreviacao=f"UE-{codigo_ue}",
                        )
                        self.db.session.add(ue)
                        self.db.session.flush()
                    relacionamentos["ue"][codigo_ue] = ue

            # Cria transações
            for _, row in chunk.iterrows():
                sigla_uf = str(row["CO_UF"]).strip().upper()
                codigo_ncm = str(row["CO_NCM"])

                transacao = Transacao(
                    codigo=f"TRANS-{row['CO_ANO']}-{row['CO_MES']}-{row.name}",
                    nome=f"Transação {row['CO_NCM']}",
                    ano=int(row["CO_ANO"]),
                    mes=int(row["CO_MES"]),
                    quantidade=int(row["QT_ESTAT"]),
                    peso=int(row["KG_LIQUIDO"]),
                    valor=int(row["VL_FOB"]),
                    ncm=relacionamentos["ncm"][codigo_ncm],
                    uf=relacionamentos["uf"][sigla_uf],
                    via=relacionamentos["via"][int(row["CO_VIA"])],
                    urf=relacionamentos["urf"][int(row["CO_URF"])],
                    ue=relacionamentos["ue"][int(row["CO_UNID"])],
                    pais=relacionamentos["pais"][int(row["CO_PAIS"])],
                )
                transacoes.append(transacao)

            try:
                self.db.session.add_all(transacoes)
                self.db.session.commit()
            except Exception as e:
                self.db.session.rollback()
                print(f"Erro ao salvar transações: {str(e)}")
                raise


def importar(db: SQLAlchemy):
    loader = DataLoader(db)

    dados_2024 = loader.processar_arquivo_2024()

    if dados_2024 is not None:
        loader.carregar_dados(dados_2024)
        print("Dados carregados com sucesso!")

    # versao para todos os anos (2nd sprint)
    # dados_todos_anos = loader.processar_todos_anos()
    # if dados_todos_anos is not None:
    #     loader.carregar_dados(dados_todos_anos)

    # # versao para todos os anos (2nd sprint)
    # def processar_todos_anos(self):
    #     dfs_filtrados = []
    #     for year in YEARS:
    #         try:
    #             url = f"{BASE_URL}{TIPO}_{year}.csv"
    #             print(f"Processando {TIPO} {year}...")

    #             df = pd.read_csv(url, sep=";", encoding="latin1")
    #             df_filtrado = self.aplicar_filtros(df)
    #             dfs_filtrados.append(df_filtrado)

    #             print(f"Concluído: {year} ({len(df_filtrado)} registros)")
    #         except Exception as e:
    #             print(f"Erro ao processar {year}: {str(e)}")

    #     if dfs_filtrados:
    #         return pd.concat(dfs_filtrados, ignore_index=True)
    #     return None


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        db = SQLAlchemy.get_instance()

        importar(db)
