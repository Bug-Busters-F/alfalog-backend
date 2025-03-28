from src.core.base import BaseModel
from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.ncms.model import NCMModel
from src.paises.model import PaisModel
from src.ues.model import UEModel
from src.ufs.model import UFModel
from src.urfs.model import URFModel
from src.vias.model import ViaModel


class TransacaoModel(BaseModel):
    """Model da Transação."""

    __tablename__ = "transacoes"

    id: Mapped[int] = mapped_column(primary_key=True)
    codigo: Mapped[str] = mapped_column(String(31), unique=True)
    nome: Mapped[str] = mapped_column(String(255))
    ano: Mapped[int] = mapped_column(Integer)
    mes: Mapped[int] = mapped_column(Integer)
    quantidade: Mapped[int] = mapped_column(Integer)
    peso: Mapped[int] = mapped_column(Integer)
    valor: Mapped[int] = mapped_column(Integer)

    # FKs
    ncm_id: Mapped[int] = mapped_column(ForeignKey(NCMModel.id, ondelete="CASCADE"))
    ncm: Mapped[NCMModel] = relationship(back_populates="transacoes")
    ue_id: Mapped[int] = mapped_column(ForeignKey(UEModel.id, ondelete="CASCADE"))
    ue: Mapped[UEModel] = relationship(back_populates="transacoes")
    pais_id: Mapped[int] = mapped_column(ForeignKey(PaisModel.id, ondelete="CASCADE"))
    pais: Mapped[PaisModel] = relationship(back_populates="transacoes")
    uf_id: Mapped[int] = mapped_column(ForeignKey(UFModel.id, ondelete="CASCADE"))
    uf: Mapped[UFModel] = relationship(back_populates="transacoes")
    via_id: Mapped[int] = mapped_column(ForeignKey(ViaModel.id, ondelete="CASCADE"))
    via: Mapped[ViaModel] = relationship(back_populates="transacoes")
    urf_id: Mapped[int] = mapped_column(ForeignKey(URFModel.id, ondelete="CASCADE"))
    urf: Mapped[URFModel] = relationship(back_populates="transacoes")

    def __repr__(self):
        return f"Transação: código = {self.codigo!r}, nome = {self.nome!r}, \
            ano = {self.ano!r}, mes = {self.mes!r}, quantidade = {self.quantidade!r}, peso = {self.peso!r}, valor = {self.valor!r}, \
            ncm_id = {self.ncm_id!r}, ue_id = {self.ue_id!r}, pais_id = {self.pais_id!r}, uf_id = {self.uf_id!r}, via_id = {self.via_id!r}, \
            urf_id = {self.urf_id!r}."
