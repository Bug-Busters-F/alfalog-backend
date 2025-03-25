from src.core.base import BaseModel
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column


class UFModel(BaseModel):
    """Model da Unidade Federativa (UF)."""

    __tablename__ = "ufs"

    id: Mapped[int] = mapped_column(primary_key=True)
    codigo: Mapped[str] = mapped_column(String(31), unique=True)
    nome: Mapped[str] = mapped_column(String(255))
    sigla: Mapped[str] = mapped_column(String(255))
    nome_regiao: Mapped[str] = mapped_column(String(255))

    def __repr__(self):
        return f"Unidade Federativa: código = {self.codigo}, nome = {self.nome}, sigla = {self.sigla}, nome da região = {self.nome_regiao}."
