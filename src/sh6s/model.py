from src.core.base import BaseModel
from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column


class SH6Model(BaseModel):
    """Model da Sistema Harmonizado de Designação e Codificação de Mercadorias, na versão de 6 dígitos (SH6)."""

    __tablename__ = "sh6s"

    id: Mapped[int] = mapped_column(primary_key=True)
    codigo: Mapped[str] = mapped_column(String(31), unique=True)
    nome: Mapped[str] = mapped_column(Text)

    def __repr__(self):
        return f"SH6: código = {self.codigo!r}, nome = {self.nome!r}."
