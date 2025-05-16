import pandas as pd
from src import create_app
from src.utils.sqlalchemy import SQLAlchemy
from sqlalchemy import text
from tqdm import tqdm
from datetime import datetime
from src.somas.model import SomaModel


class DataLoader:
    def __init__(self, db):
        self.db = db
        self._load_reference_ids()

    def _load_reference_ids(self):
        with self.db.engine.connect() as conn:
            self.ncm_map = pd.read_sql("SELECT id, descricao FROM ncms", conn).set_index('descricao')['id'].to_dict()
            self.pais_map = pd.read_sql("SELECT id, nome FROM paises", conn).set_index('nome')['id'].to_dict()
            self.uf_map = pd.read_sql("SELECT id, nome FROM ufs", conn).set_index('nome')['id'].to_dict()
            self.via_map = pd.read_sql("SELECT id, nome FROM vias", conn).set_index('nome')['id'].to_dict()
            self.urf_map = pd.read_sql("SELECT id, nome FROM urfs", conn).set_index('nome')['id'].to_dict()

    def insert_bulk_data(self, df, table_name, chunk_size=100000):
        engine = self.db.engine
        total_rows = len(df)

        with tqdm(total=total_rows, desc=f"Inserindo em '{table_name}'") as pbar:
            for i in range(0, total_rows, chunk_size):
                chunk = df.iloc[i:i + chunk_size].copy()  # Cria uma cópia explícita
                chunk.loc[:, 'created_at'] = datetime.now()
                values = chunk.to_dict(orient='records')

                sql = text(f"""
                    INSERT INTO {table_name} 
                    (ano, mes, ncm_id, pais_id, uf_id, via_id, urf_id, peso, valor, created_at)
                    VALUES (:ano, :mes, :ncm_id, :pais_id, :uf_id, :via_id, :urf_id, :peso, :valor, :created_at)
                """)

                with engine.begin() as conn:
                    conn.execute(sql, values)

                pbar.update(len(chunk))


def importar_dados(db, caminho_csv, tipo_dado='importacoes'):
    loader = DataLoader(db)
    chunksize = 100_000
    dfs_processed = []

    for chunk in tqdm(pd.read_csv(caminho_csv, chunksize=chunksize), desc="Processando CSV"):
        chunk['ncm_id'] = chunk['NO_NCM_POR'].map(loader.ncm_map)
        chunk['pais_id'] = chunk['NO_PAIS'].map(loader.pais_map)
        chunk['uf_id'] = chunk['NO_UF'].map(loader.uf_map)
        chunk['via_id'] = chunk['NO_VIA'].map(loader.via_map)
        chunk['urf_id'] = chunk['NO_URF'].map(loader.urf_map)
        chunk = chunk.dropna(subset=['ncm_id', 'pais_id', 'uf_id', 'via_id', 'urf_id'])

        df_processed = pd.DataFrame({
            'ano': chunk['ANO'],
            'mes': chunk['CO_MES'],
            'ncm_id': chunk['ncm_id'].astype(int),
            'pais_id': chunk['pais_id'],
            'uf_id': chunk['uf_id'],
            'via_id': chunk['via_id'],
            'urf_id': chunk['urf_id'],
            'peso': chunk['KG_LIQUIDO'].fillna(0).astype('int64'),
            'valor': chunk['VL_FOB'].fillna(0).astype('int64'),
        })

        df_processed = df_processed.astype({
            'ano': 'int32',
            'mes': 'int32',
            'ncm_id': 'int32',
            'pais_id': 'int32',
            'uf_id': 'int32',
            'via_id': 'int32',
            'urf_id': 'int32'
        })

        dfs_processed.append(df_processed)

    df_final = pd.concat(dfs_processed, ignore_index=True)
    loader.insert_bulk_data(df_final, tipo_dado)

def calcular_somas_por_uf_e_ano_csv(db, caminho_csv_imp: str, caminho_csv_exp: str, replace: bool = False):
    df_imp = pd.read_csv(caminho_csv_imp, usecols=["ANO", "NO_UF", "VL_FOB", "KG_LIQUIDO"])
    df_exp = pd.read_csv(caminho_csv_exp, usecols=["ANO", "NO_UF", "VL_FOB", "KG_LIQUIDO"])

    # Remove registros com KG_LIQUIDO zero ou nulo para evitar divisão por zero
    df_imp = df_imp[df_imp["KG_LIQUIDO"] > 0]
    df_exp = df_exp[df_exp["KG_LIQUIDO"] > 0]

    # Calcula o novo valor por quilo
    df_imp["VL_AGREGADO"] = df_imp["VL_FOB"] / df_imp["KG_LIQUIDO"]
    df_exp["VL_AGREGADO"] = df_exp["VL_FOB"] / df_exp["KG_LIQUIDO"]

    # Agrupamento e agregação
    grupo_imp = df_imp.groupby(["ANO", "NO_UF"]).agg(
        numero_total_importacoes=("VL_FOB", "count"),
        valor_agregado_total_importacao_reais=("VL_AGREGADO", "sum")
    ).reset_index()

    grupo_exp = df_exp.groupby(["ANO", "NO_UF"]).agg(
        numero_total_exportacao=("VL_FOB", "count"),
        valor_agregado_total_exportacao_reais=("VL_AGREGADO", "sum")
    ).reset_index()

    grupo_imp.rename(columns={"NO_UF": "estado", "ANO": "ano"}, inplace=True)
    grupo_exp.rename(columns={"NO_UF": "estado", "ANO": "ano"}, inplace=True)

    df_final = pd.merge(grupo_exp, grupo_imp, on=["estado", "ano"], how="outer").fillna(0)
    df_final["numero_total_exportacao"] = df_final["numero_total_exportacao"].astype(int)
    df_final["numero_total_importacoes"] = df_final["numero_total_importacoes"].astype(int)
    df_final["valor_agregado_total_exportacao_reais"] = df_final["valor_agregado_total_exportacao_reais"].astype(int).astype(str)
    df_final["valor_agregado_total_importacao_reais"] = df_final["valor_agregado_total_importacao_reais"].astype(int).astype(str)
    df_final["ano"] = df_final["ano"].astype(str)

    # Constrói objetos da tabela `somas`
    registros = []
    for _, row in df_final.iterrows():
        registro = SomaModel(
            estado=row["estado"],
            ano=row["ano"],
            numero_total_exportacao=row["numero_total_exportacao"],
            numero_total_importacoes=row["numero_total_importacoes"],
            valor_agregado_total_exportacao_reais=row["valor_agregado_total_exportacao_reais"],
            valor_agregado_total_importacao_reais=row["valor_agregado_total_importacao_reais"]
        )
        registros.append(registro)

    # Salva no banco
    with db.session.begin():
        if replace:
            db.session.query(SomaModel).delete()
        db.session.add_all(registros)

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        db = SQLAlchemy.get_instance()
        # chame as funcoes no /comex.py
        # aqui somente exemplos
        # calcular_somas_por_uf_e_ano(db)
        # importar_dados(db, "./data/dados_comex_EXP_2014_2024.csv", 'exportacoes')
        # importar_dados(db, "./data/dados_comex_IMP_2014_2024.csv", 'importacoes')
