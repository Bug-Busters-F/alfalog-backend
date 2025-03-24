from src.core.base import BaseModel
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column


class PaisModel(BaseModel):
    """Model do País."""

    __tablename__ = "paises"

    id: Mapped[int] = mapped_column(primary_key=True)
    codigo: Mapped[str] = mapped_column(String(31), unique=True)
    nome: Mapped[str] = mapped_column(String(255))

    def __repr__(self):
        return f"País: código = {self.codigo}, nome = {self.nome}."
