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


class ImportacaoModel(BaseModel):
    """Model da Transação."""

    __tablename__ = "importacoes"

    id: Mapped[int] = mapped_column(primary_key=True)
    codigo: Mapped[str] = mapped_column(String(31), unique=True)
    nome: Mapped[str] = mapped_column(String(255))
    ano: Mapped[int] = mapped_column(Integer)
    mes: Mapped[int] = mapped_column(Integer)
    quantidade: Mapped[int] = mapped_column(BigInteger)
    peso: Mapped[int] = mapped_column(BigInteger)
    valor: Mapped[int] = mapped_column(BigInteger)

    # FKs
    ncm_id: Mapped[int] = mapped_column(ForeignKey(NCMModel.id, ondelete="CASCADE"))
    ncm: Mapped[NCMModel] = relationship(back_populates="importacoes")
    ue_id: Mapped[int] = mapped_column(ForeignKey(UEModel.id, ondelete="CASCADE"))
    ue: Mapped[UEModel] = relationship(back_populates="importacoes")
    pais_id: Mapped[int] = mapped_column(ForeignKey(PaisModel.id, ondelete="CASCADE"))
    pais: Mapped[PaisModel] = relationship(back_populates="importacoes")
    uf_id: Mapped[int] = mapped_column(ForeignKey(UFModel.id, ondelete="CASCADE"))
    uf: Mapped[UFModel] = relationship(back_populates="importacoes")
    via_id: Mapped[int] = mapped_column(ForeignKey(ViaModel.id, ondelete="CASCADE"))
    via: Mapped[ViaModel] = relationship(back_populates="importacoes")
    urf_id: Mapped[int] = mapped_column(ForeignKey(URFModel.id, ondelete="CASCADE"))
    urf: Mapped[URFModel] = relationship(back_populates="importacoes")

    @hybrid_property
    def valor_agregado(self):
        if self.peso == 0:  # Prevent division by zero
            return None
        return round(self.valor / self.peso, 2)

    @valor_agregado.expression
    def valor_agregado(cls):
        return func.round(cls.valor / cls.peso, 2)

    def __repr__(self):
        return f"Transação: código = {self.codigo!r}, nome = {self.nome!r}, \
            ano = {self.ano!r}, mes = {self.mes!r}, quantidade = {self.quantidade!r}, peso = {self.peso!r}, valor = {self.valor!r}, \
            valor agregado = {self.valor_agregado!r}, ncm_id = {self.ncm_id!r}, ue_id = {self.ue_id!r}, pais_id = {self.pais_id!r}, \
            uf_id = {self.uf_id!r}, via_id = {self.via_id!r}, urf_id = {self.urf_id!r}."
