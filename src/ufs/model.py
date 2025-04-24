from typing import List
from src.core.base import BaseModel
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship


class UFModel(BaseModel):
    """Model da Unidade Federativa (UF)."""

    __tablename__ = "ufs"

    id: Mapped[int] = mapped_column(primary_key=True)
    codigo: Mapped[str] = mapped_column(String(31), unique=True)
    nome: Mapped[str] = mapped_column(String(255))
    sigla: Mapped[str] = mapped_column(String(255))
    nome_regiao: Mapped[str] = mapped_column(String(255))

    # FK
    exportacoes: Mapped[List["ExportacaoModel"]] = relationship(
        back_populates="uf", cascade="all, delete-orphan"
    )
    importacoes: Mapped[List["ImportacaoModel"]] = relationship(
        back_populates="uf", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"Unidade Federativa: código = {self.codigo!r}, nome = {self.nome!r}, sigla = {self.sigla!r}, nome da região = {self.nome_regiao!r}."
