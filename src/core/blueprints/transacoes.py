# Rota de transações unindo exportações e importações via UNION ALL
from flask import Blueprint, request, jsonify, current_app
from sqlalchemy import and_, func, literal
from sqlalchemy.sql import union_all
from sqlalchemy.orm import aliased
from src.exportacoes.model import ExportacaoModel
from src.importacoes.model import ImportacaoModel
from src.ncms.model import NCMModel
from src.paises.model import PaisModel
from src.ufs.model import UFModel
from src.vias.model import ViaModel
from src.urfs.model import URFModel
from src.ues.model import UEModel
from src.utils.sqlalchemy import SQLAlchemy
from math import ceil

transacoes_bp = Blueprint('transacoes', __name__, url_prefix='/api/transacoes')

@transacoes_bp.route('/', methods=['GET'])
def listar_transacoes():
    try:
        # Parâmetros de query
        coAno     = request.args.get('coAno')
        coMes     = request.args.get('coMes')
        coPais    = request.args.get('coPais')
        coNcm     = request.args.get('coNcm')
        sgUfNcm   = request.args.get('sgUfNcm')
        coVia     = request.args.get('coVia')
        coUrf     = request.args.get('coUrf')
        searchNcm = request.args.get('searchNcm')
        sortBy    = request.args.get('sortBy', 'ano')
        sortOrder = request.args.get('sortOrder', 'asc')

        try:
            page    = int(request.args.get('page', 1))
            perPage = int(request.args.get('perPage', 10))
        except ValueError:
            return jsonify({'error': 'page e perPage devem ser números inteiros'}), 400

        db = SQLAlchemy.get_instance()
        current_app.logger.debug(f"Args: {request.args.to_dict()}")

        # Validação: ao menos um filtro ou searchNcm
        if not any([coAno, coMes, coPais, coNcm, sgUfNcm, coVia, coUrf, searchNcm]):
            return jsonify({'error': 'Informe ao menos um filtro ou searchNcm'}), 400

        # Conversão helper
        def to_int(val):
            try:
                return int(val)
            except (TypeError, ValueError):
                return None

        # Monta filtros para exportações
        filtros_exp = []
        if coAno and (v := to_int(coAno)) is not None:
            filtros_exp.append(ExportacaoModel.ano == v)
        if coMes and (v := to_int(coMes)) is not None:
            filtros_exp.append(ExportacaoModel.mes == v)
        if coPais and (v := to_int(coPais)) is not None:
            filtros_exp.append(ExportacaoModel.pais_id == v)
        if coNcm and (v := to_int(coNcm)) is not None:
            filtros_exp.append(ExportacaoModel.ncm_id == v)
        if sgUfNcm and (v := to_int(sgUfNcm)) is not None:
            filtros_exp.append(ExportacaoModel.uf_id == v)
        if coVia and (v := to_int(coVia)) is not None:
            filtros_exp.append(ExportacaoModel.via_id == v)
        if coUrf and (v := to_int(coUrf)) is not None:
            filtros_exp.append(ExportacaoModel.urf_id == v)
        if searchNcm:
            filtros_exp.append(
                ExportacaoModel.ncm.has(
                    NCMModel.codigo.like(f"%{searchNcm}%")
                )
            )

        # Monta filtros para importações
        filtros_imp = []
        if coAno and (v := to_int(coAno)) is not None:
            filtros_imp.append(ImportacaoModel.ano == v)
        if coMes and (v := to_int(coMes)) is not None:
            filtros_imp.append(ImportacaoModel.mes == v)
        if coPais and (v := to_int(coPais)) is not None:
            filtros_imp.append(ImportacaoModel.pais_id == v)
        if coNcm and (v := to_int(coNcm)) is not None:
            filtros_imp.append(ImportacaoModel.ncm_id == v)
        if sgUfNcm:
            filtros_imp.append(ImportacaoModel.uf_id == sgUfNcm)
        if sgUfNcm and (v := to_int(sgUfNcm)) is not None:
            filtros_imp.append(ImportacaoModel.uf_id == v)
        if coVia and (v := to_int(coVia)) is not None:
            filtros_imp.append(ImportacaoModel.via_id == v)
        if coUrf and (v := to_int(coUrf)) is not None:
            filtros_imp.append(ImportacaoModel.urf_id == v)
        if searchNcm:
            filtros_imp.append(
                ImportacaoModel.ncm.has(
                    NCMModel.codigo.like(f"%{searchNcm}%")
                )
            )

        # Configura paginação e cap
        perPage = max(1, perPage)
        page    = max(1, page)
        offset  = (page - 1) * perPage


        # Define aliases para relacionamentos
        NCMExp = aliased(NCMModel)
        PaisExp = aliased(PaisModel)
        UFExp = aliased(UFModel)
        ViaExp = aliased(ViaModel)
        URFExp = aliased(URFModel)

        NCMImp = aliased(NCMModel)
        PaisImp = aliased(PaisModel)
        UFImp = aliased(UFModel)
        ViaImp = aliased(ViaModel)
        URFImp = aliased(URFModel)

        # Query exportações com joins nas relações
        q_exp = (
            db.session.query(
                ExportacaoModel.id.label('id'),
                ExportacaoModel.ano.label('ano'),
                ExportacaoModel.mes.label('mes'),
                NCMExp.codigo.label('ncm'),
                PaisExp.nome.label('pais'),
                UFExp.sigla.label('uf'),
                ViaExp.nome.label('via'),
                URFExp.codigo.label('urf'),
                ExportacaoModel.peso.label('peso'),
                ExportacaoModel.valor.label('valor'),
                literal('exportacao').label('tipo')
            )
            .join(NCMExp, ExportacaoModel.ncm)
            .join(PaisExp, ExportacaoModel.pais)
            .join(UFExp, ExportacaoModel.uf)
            .join(ViaExp, ExportacaoModel.via)
            .join(URFExp, ExportacaoModel.urf)
        )
        if filtros_exp:
            q_exp = q_exp.filter(and_(*filtros_exp))

        # Query importações com joins nas relações
        q_imp = (
            db.session.query(
                ImportacaoModel.id.label('id'),
                ImportacaoModel.ano.label('ano'),
                ImportacaoModel.mes.label('mes'),
                NCMImp.codigo.label('ncm'),
                PaisImp.nome.label('pais'),
                UFImp.sigla.label('uf'),
                ViaImp.nome.label('via'),
                URFImp.codigo.label('urf'),
                ImportacaoModel.peso.label('peso'),
                ImportacaoModel.valor.label('valor'),
                literal('importacao').label('tipo')
            )
            .join(NCMImp, ImportacaoModel.ncm)
            .join(PaisImp, ImportacaoModel.pais)
            .join(UFImp, ImportacaoModel.uf)
            .join(ViaImp, ImportacaoModel.via)
            .join(URFImp, ImportacaoModel.urf)
        )
        if filtros_imp:
            q_imp = q_imp.filter(and_(*filtros_imp))

        # União das queries
        stmt_exp = q_exp.statement
        stmt_imp = q_imp.statement
        union_stmt = union_all(stmt_exp, stmt_imp).alias('u')

        # Ordenação
        valid_sort_fields = {'id', 'ano', 'mes', 'ncm', 'pais', 'uf', 'via', 'urf', 'peso', 'valor', 'tipo'}
        if sortBy not in valid_sort_fields:
            sortBy = 'ano'
        order_column = getattr(union_stmt.c, sortBy)
        order_clause = order_column.asc() if sortOrder == 'asc' else order_column.desc()

        # Conta total filtrado
        total = db.session.query(func.count()).select_from(union_stmt).scalar() or 0
        total_count = total
        totalPages = ceil(total_count / perPage) if total_count > 0 else 1

        # Paginação e ordenação
        results = (
            db.session.query(
                union_stmt.c.id,
                union_stmt.c.ano,
                union_stmt.c.mes,
                union_stmt.c.ncm,
                union_stmt.c.pais,
                union_stmt.c.uf,
                union_stmt.c.via,
                union_stmt.c.urf,
                union_stmt.c.peso,
                union_stmt.c.valor,
                union_stmt.c.tipo
            )
            .select_from(union_stmt)
            .order_by(order_clause)
            .limit(perPage)
            .offset(offset)
            .all()
        )

        # Serializa resposta
        data = [
            {col: getattr(row, col) for col in ['id','ano','mes','ncm','pais','uf','via','urf','peso','valor','tipo']}
            for row in results
        ]

        return jsonify({
            'data':       data,
            'page':       page,
            'perPage':    perPage,
            'totalPages': totalPages,
            'totalCount': total_count
        }), 200

    except Exception as e:
        current_app.logger.error('Erro ao listar transações', exc_info=e)
        return jsonify({'error': str(e)}), 500
    
@transacoes_bp.route('/distinct', methods=['GET'])
def distinct_field():
    field = request.args.get('field')
    db = SQLAlchemy.get_instance()

    # Valores para campos numéricos (ano, mês)
    if field == 'coAno':
        vals_exp = [v[0] for v in db.session.query(ExportacaoModel.ano).distinct().all()]
        vals_imp = [v[0] for v in db.session.query(ImportacaoModel.ano).distinct().all()]
        combined = sorted({*vals_exp, *vals_imp})
        # Retorna lista de objetos id/label
        return jsonify({'values': [{'id': v, 'label': str(v)} for v in combined]}), 200

    if field == 'coMes':
        vals_exp = [v[0] for v in db.session.query(ExportacaoModel.mes).distinct().all()]
        vals_imp = [v[0] for v in db.session.query(ImportacaoModel.mes).distinct().all()]
        combined = sorted({*vals_exp, *vals_imp})
        return jsonify({'values': [{'id': v, 'label': str(v)} for v in combined]}), 200

    # Campos relacionais: país, UF, via, URF
    rel_map = {
        'coPais':  (PaisModel, ExportacaoModel.pais,  ImportacaoModel.pais,  'nome'),
        'sgUfNcm': (UFModel,   ExportacaoModel.uf,    ImportacaoModel.uf,    'sigla'),
        'coVia':   (ViaModel,  ExportacaoModel.via,   ImportacaoModel.via,   'nome'),
        'coUrf':   (URFModel,  ExportacaoModel.urf,   ImportacaoModel.urf,   'codigo')
    }
    if field in rel_map:
        Model, exp_rel, imp_rel, attr = rel_map[field]
        exp = (
            db.session
              .query(Model.id, getattr(Model, attr))
              .join(exp_rel)
              .distinct()
              .all()
        )
        imp = (
            db.session
              .query(Model.id, getattr(Model, attr))
              .join(imp_rel)
              .distinct()
              .all()
        )
        # Retorna lista de objetos
        combined = sorted({(id, label) for id, label in exp + imp}, key=lambda x: str(x[1]))
        values = [{'id': id, 'label': label} for id, label in combined]
        return jsonify({'values': values}), 200
    
    return jsonify({'error': 'field inválido'}), 400