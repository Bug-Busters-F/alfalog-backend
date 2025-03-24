from src.core.base import BaseModel
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column


class URFModel(BaseModel):
    """Model da Unidade da Receita Federal (URF)."""

    __tablename__ = "urfs"

    id: Mapped[int] = mapped_column(primary_key=True)
    codigo: Mapped[str] = mapped_column(String(31), unique=True)
    nome: Mapped[str] = mapped_column(String(255))

    def __repr__(self):
        return (
            f"Unidade da Receita Federal: código = {self.codigo}, nome = {self.nome}."
        )
