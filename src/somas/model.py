from typing import List
from src.core.base import BaseModel
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship


class SomaModel(BaseModel):
    """Model de Card Soma (por Estado))."""

    __tablename__ = "somas"

    id: Mapped[int] = mapped_column(primary_key=True)
    estado: Mapped[str] = mapped_column(String(31), unique=True)
    ano: Mapped[str] = mapped_column(String(255))
    numero_total_exportacao: Mapped[int] = mapped_column(Integer(255))
    numero_total_importacoes: Mapped[int] = mapped_column(Integer(255))
    valor_total_exportacao_reais: Mapped[str] = mapped_column(String(255))
    valor_total_importacao_reais: Mapped[str] = mapped_column(String(255))

    # FK
    exportacoes: Mapped[List["ExportacaoModel"]] = relationship(
        back_populates="uf", cascade="all, delete-orphan"
    )
    importacoes: Mapped[List["ImportacaoModel"]] = relationship(
        back_populates="uf", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"Card Somas: estado = {self.estado!r}, ano = {self.ano!r}, total de exportações = {self.numero_total_exportacao!r}, total de importações = {self.numero_total_importacoes!r}, Valor total em Reais de exportações = {self.valor_total_exportacao_reais!r}, Valor total em Reais de importações = {self.valor_total_importacao_reais!r}."
