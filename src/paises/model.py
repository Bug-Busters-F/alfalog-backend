from typing import List
from src.core.base import BaseModel
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship


class PaisModel(BaseModel):
    """Model do País."""

    __tablename__ = "paises"

    id: Mapped[int] = mapped_column(primary_key=True)
    codigo: Mapped[str] = mapped_column(String(31), unique=True)
    nome: Mapped[str] = mapped_column(String(255))

    # FK
    transacoes: Mapped[List["TransacaoModel"]] = relationship(
        back_populates="pais", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"País: código = {self.codigo!r}, nome = {self.nome!r}."
