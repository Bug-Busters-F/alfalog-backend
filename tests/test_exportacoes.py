import pytest
from faker import Faker
from src.exportacoes.model import ExportacaoModel
from tests.test_ncms import create_ncm_db
from tests.test_ues import create_ue_db
from tests.test_paises import create_pais_db
from tests.test_ufs import create_uf_db
from tests.test_vias import create_via_db
from tests.test_urfs import create_urf_db

url = "/api/exportacoes/"
fake = Faker("pt_BR")


def make_exportacao_data(dependencies):
    """Create test Exportacao data with dependencies"""
    return {
        "codigo": fake.unique.bothify(text="####"),
        "nome": f"Transação {fake.unique.word().capitalize()}",
        "ano": fake.random_int(min=2000, max=2030),
        "mes": fake.random_int(min=1, max=12),
        "quantidade": fake.random_int(min=1, max=1000),
        "peso": fake.random_int(min=1, max=5000),
        "valor": fake.random_int(min=100, max=100000),
        "ncm_id": dependencies.get("ncm_id", 1),
        "ue_id": dependencies.get("ue_id", 1),
        "pais_id": dependencies.get("pais_id", 1),
        "uf_id": dependencies.get("uf_id", 1),
        "via_id": dependencies.get("via_id", 1),
        "urf_id": dependencies.get("urf_id", 1),
    }


def create_exportacao_dependencies(session):
    """Create all dependencies for Exportacao in database"""
    ncm = create_ncm_db(session)
    ue = create_ue_db(session)
    pais = create_pais_db(session)
    uf = create_uf_db(session)
    via = create_via_db(session)
    urf = create_urf_db(session)

    return {
        "ncm_id": ncm.id,
        "ue_id": ue.id,
        "pais_id": pais.id,
        "uf_id": uf.id,
        "via_id": via.id,
        "urf_id": urf.id,
    }


def create_exportacao_db(session, data=None, dependencies=None) -> ExportacaoModel:
    """Create test Exportacao record with all dependencies"""
    dependencies = dependencies or create_exportacao_dependencies(session)
    exportacao_data = data or make_exportacao_data(dependencies)

    exportacao = ExportacaoModel(**exportacao_data)
    session.add(exportacao)
    session.commit()
    return exportacao


class TestExportacaoCollection:
    def test_get_empty(self, client):
        """Test Retrieve all entries when database is empty is successful."""
        response = client.get(url)
        assert response.status_code == 200
        assert response.json == []

    def test_list_with_data(self, client, session):
        """Test Retrieve all entries when database has data is successful."""
        created_exportacao = create_exportacao_db(session)

        response = client.get(url)
        assert response.status_code == 200
        assert isinstance(response.json, list)
        assert len(response.json) > 0

        listed_exportacao = response.json[0]["data"]
        assert listed_exportacao["id"] == created_exportacao.id
        assert listed_exportacao["nome"] == created_exportacao.nome

    def test_create_valid(self, client, session):
        """Test creating a valid Exportacao"""
        dependencies = create_exportacao_dependencies(session)
        exportacao_data = make_exportacao_data(dependencies)

        response = client.post(url, json=exportacao_data)

        assert response.status_code == 201
        assert response.json["data"]["nome"] == exportacao_data["nome"]
        assert response.json["data"]["codigo"] == exportacao_data["codigo"]
        assert response.json["data"]["ano"] == exportacao_data["ano"]
        assert response.json["data"]["mes"] == exportacao_data["mes"]
        assert response.json["data"]["quantidade"] == exportacao_data["quantidade"]
        assert response.json["data"]["peso"] == exportacao_data["peso"]
        assert response.json["data"]["valor"] == exportacao_data["valor"]
        assert isinstance(response.json["data"]["id"], int)

        # Verify database
        db_exportacao = (
            session.query(ExportacaoModel)
            .filter_by(id=response.json["data"]["id"])
            .first()
        )
        assert db_exportacao is not None
        assert db_exportacao.codigo == exportacao_data["codigo"]

    def test_create_duplicate(self, client, session):
        """Test Create an entry with an existing codigo fails."""
        exportacao_data = make_exportacao_data(create_exportacao_dependencies(session))
        create_exportacao_db(session, exportacao_data)
        response = client.post(url, json=exportacao_data)

        assert response.status_code == 422
        assert "Já existe uma Exportacao com esse código" in response.json["message"]

    @pytest.mark.parametrize(
        "payload, missing_field",
        [
            ({"codigo": "1234"}, "nome"),
            ({"nome": "Exportacao Test"}, "codigo"),
            ({}, "nome"),
        ],
    )
    def test_create_missing_fields(self, client, payload, missing_field, session):
        """Test validation for missing required fields"""
        dependencies = create_exportacao_dependencies(session)
        payload.update(
            {
                "ncm_id": dependencies["ncm_id"],
                "ue_id": dependencies["ue_id"],
                "pais_id": dependencies["pais_id"],
                "uf_id": dependencies["uf_id"],
                "via_id": dependencies["via_id"],
                "urf_id": dependencies["urf_id"],
            }
        )

        response = client.post(url, json=payload)

        assert response.status_code == 400
        assert "message" in response.json
        assert missing_field in response.json["message"]


class TestExportacaoResource:
    """Tests for single Exportacao resource endpoints (/api/exportacoes/<id>)"""

    @pytest.fixture
    def existing_exportacao(self, session) -> ExportacaoModel:
        """Fixture providing an existing Exportacao."""
        return create_exportacao_db(session)

    def test_get_existing(self, client, existing_exportacao):
        """Test getting an existing Exportacao."""
        response = client.get(f"{url}{existing_exportacao.id}")

        assert response.status_code == 200
        assert response.json["data"]["id"] == existing_exportacao.id
        assert response.json["data"]["nome"] == existing_exportacao.nome
        assert response.json["data"]["codigo"] == existing_exportacao.codigo
        assert response.json["data"]["ano"] == existing_exportacao.ano
        assert response.json["data"]["mes"] == existing_exportacao.mes
        assert response.json["data"]["quantidade"] == existing_exportacao.quantidade
        assert response.json["data"]["peso"] == existing_exportacao.peso
        assert response.json["data"]["valor"] == existing_exportacao.valor

    def test_get_nonexistent(self, client):
        """Test getting non-existent Exportacao."""
        response = client.get(f"{url}9999")
        assert response.status_code == 404
        assert "Nenhum registro encontrado" in response.json["message"]

    def test_update_same_codigo(self, client, existing_exportacao, session):
        """Test Update an existing entry with same codigo is successful."""
        dependencies = create_exportacao_dependencies(session)
        update_data = {
            "nome": "Updated Exportacao",
            "codigo": existing_exportacao.codigo,
            "ano": 2026,
            "mes": 4,
            "quantidade": 40,
            "peso": 50,
            "valor": 200,
            "ncm_id": dependencies["ncm_id"],
            "ue_id": dependencies["ue_id"],
            "pais_id": dependencies["pais_id"],
            "uf_id": dependencies["uf_id"],
            "via_id": dependencies["via_id"],
            "urf_id": dependencies["urf_id"],
        }
        response = client.put(f"{url}{existing_exportacao.id}", json=update_data)
        assert response.status_code == 204

        # Verify update
        session.refresh(existing_exportacao)
        assert existing_exportacao.nome == update_data["nome"]
        assert existing_exportacao.codigo == update_data["codigo"]
        assert existing_exportacao.ano == update_data["ano"]
        assert existing_exportacao.mes == update_data["mes"]
        assert existing_exportacao.quantidade == update_data["quantidade"]
        assert existing_exportacao.peso == update_data["peso"]
        assert existing_exportacao.valor == update_data["valor"]

    def test_update_different_codigo(self, client, existing_exportacao, session):
        """Test Update an existing entry with different codigo is successful."""
        dependencies = create_exportacao_dependencies(session)
        update_data = {
            "nome": "Updated Exportacao",
            "codigo": "5678",
            "ano": 2026,
            "mes": 4,
            "quantidade": 40,
            "peso": 50,
            "valor": 200,
            "ncm_id": dependencies["ncm_id"],
            "ue_id": dependencies["ue_id"],
            "pais_id": dependencies["pais_id"],
            "uf_id": dependencies["uf_id"],
            "via_id": dependencies["via_id"],
            "urf_id": dependencies["urf_id"],
        }
        response = client.put(f"{url}{existing_exportacao.id}", json=update_data)
        assert response.status_code == 204

        # Verify update
        session.refresh(existing_exportacao)
        assert existing_exportacao.nome == update_data["nome"]
        assert existing_exportacao.codigo == update_data["codigo"]

    def test_update_nonexistent(self, client, session):
        """Test updating non-existent Exportacao"""
        dependencies = create_exportacao_dependencies(session)
        exportacao_data = make_exportacao_data(dependencies)
        response = client.put(f"{url}9999", json=exportacao_data)

        assert response.status_code == 404
        assert "Nenhum registro encontrado" in response.json["message"]

    def test_update_existent_codigo(self, client, existing_exportacao, session):
        """Test updating with an existent codigo fails."""
        data = make_exportacao_data(create_exportacao_dependencies(session))
        exportacao2 = create_exportacao_db(session, data)

        data["codigo"] = existing_exportacao.codigo
        response = client.put(f"{url}{exportacao2.id}", json=data)

        assert response.status_code == 422
        assert "Já existe uma Exportacao com esse código" in response.json["message"]

    def test_delete_existing(self, client, existing_exportacao, session):
        """Test deleting existing Exportacao"""
        response = client.delete(f"{url}{existing_exportacao.id}")

        assert response.status_code == 204

        # Verify deletion
        assert session.get(ExportacaoModel, existing_exportacao.id) is None

    def test_delete_nonexistent(self, client):
        """Test deleting non-existent Exportacao"""
        response = client.delete(f"{url}9999")

        assert response.status_code == 404
        assert "Nenhum registro encontrado" in response.json["message"]
