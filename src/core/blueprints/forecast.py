from flask_restful import marshal_with
from flask import Blueprint
from ...utils.sqlalchemy import SQLAlchemy
from src.forecasts.exportacoes.model import ForecastExportacaoModel
from src.forecasts.importacoes.model import ForecastImportacaoModel
from src.forecasts.balanca.model import ForecastBalancaModel
from ..fields import forecast_fields

forecast = Blueprint("forecast", __name__, url_prefix="/api/forecast")


@forecast.route("/exportacoes")
@marshal_with(forecast_fields)
def exportacoes():
    """Retrieve forecast data."""
    db = SQLAlchemy.get_instance()
    entries = (
        db.session.query(ForecastExportacaoModel)
        .order_by(ForecastExportacaoModel.ds)
        .all()
    )
    return entries


@forecast.route("/importacoes")
@marshal_with(forecast_fields)
def importacoes():
    """Retrieve forecast data."""
    db = SQLAlchemy.get_instance()
    entries = (
        db.session.query(ForecastImportacaoModel)
        .order_by(ForecastImportacaoModel.ds)
        .all()
    )
    return entries


@forecast.route("/balanca-comercial")
@marshal_with(forecast_fields)
def balanca():
    """Retrieve forecast data."""
    db = SQLAlchemy.get_instance()
    entries = (
        db.session.query(ForecastBalancaModel).order_by(ForecastBalancaModel.ds).all()
    )
    return entries
