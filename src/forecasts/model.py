from typing import List
from src.core.base import BaseModel
from sqlalchemy import Integer, String, Float, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import date


class ForecastModel(BaseModel):
    """Abstract Model para forecast."""

    __abstract__ = True
    # __tablename__ = "forecasts"

    id: Mapped[int] = mapped_column(primary_key=True)
    ds: Mapped[date] = mapped_column(Date, unique=True)
    y: Mapped[float] = mapped_column(Float, nullable=True)
    yhat: Mapped[float] = mapped_column(Float, nullable=True)
    yhat_lower: Mapped[float] = mapped_column(Float, nullable=True)
    yhat_upper: Mapped[float] = mapped_column(Float, nullable=True)
    trend: Mapped[float] = mapped_column(Float, nullable=True)
    trend_lower: Mapped[float] = mapped_column(Float, nullable=True)
    trend_upper: Mapped[float] = mapped_column(Float, nullable=True)
    additive_terms: Mapped[float] = mapped_column(Float, nullable=True)
    additive_terms_lower: Mapped[float] = mapped_column(Float, nullable=True)
    additive_terms_upper: Mapped[float] = mapped_column(Float, nullable=True)
    yearly: Mapped[float] = mapped_column(Float, nullable=True)
    yearly_lower: Mapped[float] = mapped_column(Float, nullable=True)
    yearly_upper: Mapped[float] = mapped_column(Float, nullable=True)
    multiplicative_terms: Mapped[float] = mapped_column(Float, nullable=True)
    multiplicative_terms_lower: Mapped[float] = mapped_column(Float, nullable=True)
    multiplicative_terms_upper: Mapped[float] = mapped_column(Float, nullable=True)
