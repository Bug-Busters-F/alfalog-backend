from src.core.base import BaseModel
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column


class NCMModel(BaseModel):
    """Model da Nomenclatura Comum do Mercosul (NCM)."""

    __tablename__ = "ncms"

    id: Mapped[int] = mapped_column(primary_key=True)
    codigo: Mapped[str] = mapped_column(String(31), unique=True)
    descricao: Mapped[str] = mapped_column(String(255))

    def __repr__(self):
        return f"Nomenclatura Comum do Mercosul: código = {self.codigo}, descrição = {self.descricao}."
