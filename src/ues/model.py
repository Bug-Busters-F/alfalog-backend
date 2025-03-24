from src.core.base import BaseModel
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column


class UEModel(BaseModel):
    """Model da Unidade Estatística."""

    __tablename__ = "unidades_estatisticas"

    id: Mapped[int] = mapped_column(primary_key=True)
    codigo: Mapped[str] = mapped_column(String(31), unique=True)
    nome: Mapped[str] = mapped_column(String(255))
    abreviacao: Mapped[str] = mapped_column(String(31))

    def __repr__(self):
        return f"Unidade Estatística: código = {self.codigo}, nome = {self.nome}, abreviação = {self.abreviacao}."
