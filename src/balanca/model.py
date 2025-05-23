from src.core.base import BaseModel
from sqlalchemy import ForeignKey, Integer, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.ufs.model import UFModel


class BalancaModel(BaseModel):
    """Model da Balança Comercial."""

    __tablename__ = "balanca"

    id: Mapped[int] = mapped_column(primary_key=True)
    ano: Mapped[int] = mapped_column(Integer, nullable=False)
    valor: Mapped[int] = mapped_column(BigInteger, nullable=False)

    uf_id: Mapped[int] = mapped_column(ForeignKey(UFModel.id, ondelete="CASCADE"))
    uf: Mapped[UFModel] = relationship(back_populates="balancas")


    def __repr__(self):
        return f"Balança: ano = {self.ano!r}, valor = {self.valor!r}, id_uf = {self.id_uf!r}"
