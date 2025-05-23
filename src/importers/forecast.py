from datetime import datetime
import pandas as pd
import os
from flask import current_app
from flask_sqlalchemy import SQLAlchemy
from ..forecasts.model import ForecastModel
from ..forecasts.exportacoes.model import ForecastExportacaoModel
from ..forecasts.importacoes.model import ForecastImportacaoModel
from ..forecasts.balanca.model import ForecastBalancaModel
from ..utils.sqlalchemy import SQLAlchemy
from . import BATCH_SIZE, LIMIT


FILENAME_EXP = "exportacao_forecast_prophet_suavizado.csv"
FILENAME_IMP = "importacao_forecast_prophet_suavizado.csv"
FILENAME_BALANCA = "balanca_forecast_prophet_suavizado.csv"


def open_file(filename: str) -> pd.DataFrame:
    """Open CSV file."""
    base_dir = os.path.dirname(current_app.root_path)
    csv_path = os.path.join(base_dir, "data", filename)

    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"File not found: {csv_path}")

    df = pd.read_csv(csv_path)
    return df


def _importar(df: pd.DataFrame, forecast: ForecastModel, replace: bool = False):
    """Importa dados de Previsão/Forecast de CSV.

    Args:
        df (pd.DataFrame): DataFrame containing the data.
        forecast (ForecastModel): An empty instance of the Forecast model.
        replace (bool, optional): Should erase the database table. Defaults to False.
    """
    db = SQLAlchemy.get_instance()

    cls = forecast.__class__
    if replace:
        # delete all
        db.session.query(cls).delete()
        db.session.commit()

    # para cada linha do CSV, extrai seus dados e salva no BD
    for index, row in df.iterrows():
        fore = cls()
        fore.ds = datetime.strptime(row["ds"].strip(), "%Y-%m-%d").date()
        fore.yhat = float(row["yhat"])
        fore.yhat_lower = float(row["yhat_lower"])
        fore.yhat_upper = float(row["yhat_upper"])
        fore.trend = float(row["trend"])
        fore.trend_lower = float(row["trend_lower"])
        fore.trend_upper = float(row["trend_upper"])
        fore.additive_terms = float(row["additive_terms"])
        fore.additive_terms_lower = float(row["additive_terms_lower"])
        fore.additive_terms_upper = float(row["additive_terms_upper"])
        fore.yearly = float(row["yearly"])
        fore.yearly_lower = float(row["yearly_lower"])
        fore.yearly_upper = float(row["yearly_upper"])
        fore.multiplicative_terms = float(row["multiplicative_terms"])
        fore.multiplicative_terms_lower = float(row["multiplicative_terms_lower"])
        fore.multiplicative_terms_upper = float(row["multiplicative_terms_upper"])

        db.session.add(fore)

        # Commit in batches
        if index % BATCH_SIZE == 0:
            db.session.commit()
        if index == LIMIT:
            break

    db.session.commit()


def importar_exportacoes(replace: bool = False):
    """Importa dados de Previsão/Forecast das Exportações de CSV."""
    df = open_file(FILENAME_EXP)
    _importar(df=df, forecast=ForecastExportacaoModel(), replace=replace)


def importar_importacoes(replace: bool = False):
    """Importa dados de Previsão/Forecast das Importações de CSV."""
    df = open_file(FILENAME_IMP)
    _importar(df=df, forecast=ForecastImportacaoModel(), replace=replace)


def importar_balanca(replace: bool = False):
    """Importa dados de Previsão/Forecast da Balança Comercial de CSV."""
    df = open_file(FILENAME_BALANCA)
    _importar(df=df, forecast=ForecastBalancaModel(), replace=replace)


if __name__ == "__main__":
    importar_exportacoes()
    importar_importacoes()
    importar_balanca()
