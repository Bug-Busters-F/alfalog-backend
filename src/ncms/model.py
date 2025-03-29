from src.core.base import BaseModel
from typing import List
from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship


class NCMModel(BaseModel):
    """Model da Nomenclatura Comum do Mercosul (NCM)."""

    __tablename__ = "ncms"

    id: Mapped[int] = mapped_column(primary_key=True)
    codigo: Mapped[str] = mapped_column(String(31), unique=True)
    descricao: Mapped[str] = mapped_column(Text)

    # FK
    transacoes: Mapped[List["TransacaoModel"]] = relationship(
        back_populates="ncm", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"Nomenclatura Comum do Mercosul: código = {self.codigo!r}, descrição = {self.descricao!r}."
