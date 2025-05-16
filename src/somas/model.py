from typing import List
from src.core.base import BaseModel
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

class SomaModel(BaseModel):
    """Model de Card Soma (por Estado)."""

    __tablename__ = "somas"

    id: Mapped[int] = mapped_column(primary_key=True)
    estado: Mapped[str] = mapped_column(String(31))
    ano: Mapped[str] = mapped_column(String(255))
    numero_total_exportacao: Mapped[int] = mapped_column(Integer)
    numero_total_importacoes: Mapped[int] = mapped_column(Integer)
    valor_agregado_total_exportacao_reais: Mapped[str] = mapped_column(String(255))
    valor_agregado_total_importacao_reais: Mapped[str] = mapped_column(String(255))

    def __repr__(self):
        return f"Card Somas: estado = {self.estado!r}, ano = {self.ano!r}, total de exportações = {self.numero_total_exportacao!r}, total de importações = {self.numero_total_importacoes!r}, Valor agregado total em Reais de exportações = {self.valor_agregado_total_exportacao_reais!r}, Valor agregado total em Reais de importações = {self.valor_agregado_total_importacao_reais!r}."
