from src.utils.sqlalchemy import SQLAlchemy
from src.ufs.model import UFModel
from src.importacoes.model import ImportacaoModel
from src.exportacoes.model import ExportacaoModel
from src.balanca.model import BalancaModel
from sqlalchemy import func


def importar_balanca(db: SQLAlchemy, replace: bool = False):
    session = db.session

    ufs = session.query(UFModel).all()

    for uf in ufs:
        # Consulta agregada: total por ano
        importacoes = session.query(
            ImportacaoModel.ano,
            func.sum(ImportacaoModel.valor).label("total")
        ).filter(
            ImportacaoModel.uf_id == uf.id
        ).group_by(
            ImportacaoModel.ano
        ).all()

        exportacoes = session.query(
            ExportacaoModel.ano,
            func.sum(ExportacaoModel.valor).label("total")
        ).filter(
            ExportacaoModel.uf_id == uf.id
        ).group_by(
            ExportacaoModel.ano
        ).all()

        dict_importacoes = {i.ano: i.total for i in importacoes}
        dict_exportacoes = {e.ano: e.total for e in exportacoes}

        anos = sorted(set(dict_importacoes.keys()) | set(dict_exportacoes.keys()))

        for ano in anos:
            total_exportado = dict_exportacoes.get(ano, 0) or 0
            total_importado = dict_importacoes.get(ano, 0) or 0
            balanca_valor = total_exportado - total_importado

            if replace:
                session.query(BalancaModel).filter_by(uf_id=uf.id, ano=ano).delete()

            balanca = BalancaModel(ano=ano, valor=balanca_valor, uf=uf)
            session.add(balanca)

    session.commit()