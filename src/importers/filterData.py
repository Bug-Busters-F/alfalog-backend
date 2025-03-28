import pandas as pd
from tqdm import tqdm
from flask_sqlalchemy import SQLAlchemy
from src.ufs.model import UFModel as UF
from src.ncms.model import NCMModel as NCM
from src.paises.model import PaisModel as Pais
from src.transacoes.model import TransacaoModel as Transacao

BASE_URL = "https://balanca.economia.gov.br/balanca/bd/comexstat-bd/ncm/"
YEARS = range(2014, 2025)
TIPO = "EXP"

db = SQLAlchemy()

class DataLoader:
    def __init__(self, db_instance):
        self.db = db_instance
        
    def aplicar_filtros(self, df):
        df = df[df["CO_UNID"] != 18].copy()
        df = df[~df["CO_PAIS"].isin([0, 990, 994, 995, 997, 998, 999])].copy()
        df = df[~df["SG_UF_NCM"].isin(["ND", "ZN", "ED", "RE", "MN", "CB", "EX"])].copy()
        df = df[~df["CO_VIA"].isin([0, 3, 8, 10, 12, 13, 14, 99])].copy()
        df = df[~df["CO_URF"].isin([0, 815400, 1010109, 8110000, 9999999])].copy()
        df = df[df["QT_ESTAT"] != 0].copy()
        df = df[df["KG_LIQUIDO"] != 0].copy()
        df = df[df["VL_FOB"] != 0].copy()
        return df

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

    def carregar_dados(self, df):
        if df is None or df.empty:
            print("Nenhum dado para carregar")
            return

        chunk_size = 50000
        total_chunks = len(df) // chunk_size + (1 if len(df) % chunk_size != 0 else 0)
        
        for i in tqdm(range(total_chunks), desc="Carregando dados"):
            start_idx = i * chunk_size
            end_idx = (i + 1) * chunk_size
            chunk = df.iloc[start_idx:end_idx]
            
            transacoes = []
            relacionamentos = {'uf': {}, 'ncm': {}, 'pais': {}}
            
            # relacionamentos
            for _, row in chunk.iterrows():
                if row['CO_UF'] not in relacionamentos['uf']:
                    relacionamentos['uf'][row['CO_UF']] = self._obter_ou_criar(
                        UF, codigo=row['CO_UF'])
                if row['CO_NCM'] not in relacionamentos['ncm']:
                    relacionamentos['ncm'][row['CO_NCM']] = self._obter_ou_criar(
                        NCM, codigo=row['CO_NCM'])
                if row['CO_PAIS'] not in relacionamentos['pais']:
                    relacionamentos['pais'][row['CO_PAIS']] = self._obter_ou_criar(
                        Pais, codigo=row['CO_PAIS'])
            
            for _, row in chunk.iterrows():
                transacao = Transacao(
                    uf=relacionamentos['uf'][row['CO_UF']],
                    ncm=relacionamentos['ncm'][row['CO_NCM']],
                    pais=relacionamentos['pais'][row['CO_PAIS']],
                    vl_fob=row['VL_FOB'],
                    kg_liquido=row['KG_LIQUIDO'],
                    qt_estat=row['QT_ESTAT'],
                    co_via=row['CO_VIA'],
                    co_urf=row['CO_URF'],
                    sg_uf_ncm=row['SG_UF_NCM'],
                    co_unid=row['CO_UNID']
                )
                transacoes.append(transacao)

            self.db.session.bulk_save_objects(transacoes)
            self.db.session.commit()

    def _obter_ou_criar(self, modelo, **filtros):
        instancia = self.db.session.query(modelo).filter_by(**filtros).first()
        
        if not instancia:
            instancia = modelo(**filtros)
            self.db.session.add(instancia)
        
        return instancia

if __name__ == "__main__":
    db = SQLAlchemy.get_instance()
    loader = DataLoader(db)

    # processa apenas 2024
    dados_2024 = loader.processar_arquivo_2024()
    
    if dados_2024 is not None:
        loader.carregar_dados(dados_2024)
    
    # versao para todos os anos (2nd sprint)
    # dados_todos_anos = loader.processar_todos_anos()
    # if dados_todos_anos is not None:
    #     dados_todos_anos.to_csv(OUTPUT_FINAL, index=False, sep=";", encoding="latin1")
    #     loader.carregar_dados(dados_todos_anos)