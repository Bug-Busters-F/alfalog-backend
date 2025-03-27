from src.core.base import BaseModel
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column


class SH4Model(BaseModel):
    """Model da Sistema Harmonizado de Designação e Codificação de Mercadorias, na versão de 4 dígitos (SH4)."""

    __tablename__ = "sh4s"

    id: Mapped[int] = mapped_column(primary_key=True)
    codigo: Mapped[str] = mapped_column(String(31), unique=True)
    nome: Mapped[str] = mapped_column(String(255))

    def __repr__(self):
        return f"SH4: código = {self.codigo!r}, nome = {self.nome!r}."
