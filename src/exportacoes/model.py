from typing import Optional
from src.core.base import BaseModel
from sqlalchemy import ForeignKey, Integer, String, BigInteger, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.hybrid import hybrid_property
from src.ncms.model import NCMModel
from src.paises.model import PaisModel
from src.ues.model import UEModel
from src.ufs.model import UFModel
from src.urfs.model import URFModel
from src.vias.model import ViaModel


class ExportacaoModel(BaseModel):
    """Model da Transação."""

    __tablename__ = "exportacoes"

    id: Mapped[int] = mapped_column(primary_key=True)
    ano: Mapped[int] = mapped_column(Integer)
    mes: Mapped[int] = mapped_column(Integer)
    peso: Mapped[int] = mapped_column(BigInteger)
    valor: Mapped[int] = mapped_column(BigInteger)

    # FKs
    ncm_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey(NCMModel.id, ondelete="CASCADE"),
        nullable=True,
    )
    ncm: Mapped[NCMModel] = relationship(back_populates="exportacoes")
    ue_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey(UEModel.id, ondelete="CASCADE"),
        nullable=True,
    )
    ue: Mapped[UEModel] = relationship(back_populates="exportacoes")
    pais_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey(PaisModel.id, ondelete="CASCADE"),
        nullable=True,
    )
    pais: Mapped[PaisModel] = relationship(back_populates="exportacoes")
    uf_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey(UFModel.id, ondelete="CASCADE"),
        nullable=True,
    )
    uf: Mapped[UFModel] = relationship(back_populates="exportacoes")
    via_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey(ViaModel.id, ondelete="CASCADE"),
        nullable=True,
    )
    via: Mapped[ViaModel] = relationship(back_populates="exportacoes")
    urf_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey(URFModel.id, ondelete="CASCADE"),
        nullable=True,
    )
    urf: Mapped[URFModel] = relationship(back_populates="exportacoes")

    @hybrid_property
    def valor_agregado(self):
        if self.peso == 0:  # Prevent division by zero
            return None
        return round(self.valor / self.peso, 2)

    @valor_agregado.expression
    def valor_agregado(cls):
        return func.round(cls.valor / cls.peso, 2)

    def __repr__(self):
        return f"Transação: \
            ano = {self.ano!r}, mes = {self.mes!r}, peso = {self.peso!r}, valor = {self.valor!r}, \
            valor agregado = {self.valor_agregado!r}, ncm_id = {self.ncm_id!r}, ue_id = {self.ue_id!r}, pais_id = {self.pais_id!r}, \
            uf_id = {self.uf_id!r}, via_id = {self.via_id!r}, urf_id = {self.urf_id!r}."
