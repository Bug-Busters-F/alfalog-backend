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
        "ano": fake.random_int(min=2000, max=2030),
        "mes": fake.random_int(min=1, max=12),
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
        assert listed_exportacao["ano"] == created_exportacao.ano

    def test_create_valid(self, client, session):
        """Test creating a valid Exportacao"""
        dependencies = create_exportacao_dependencies(session)
        exportacao_data = make_exportacao_data(dependencies)

        response = client.post(url, json=exportacao_data)

        assert response.status_code == 201
        assert response.json["data"]["ano"] == exportacao_data["ano"]
        assert response.json["data"]["mes"] == exportacao_data["mes"]
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
        assert db_exportacao.ano == exportacao_data["ano"]


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
        assert response.json["data"]["ano"] == existing_exportacao.ano
        assert response.json["data"]["mes"] == existing_exportacao.mes
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
            "ano": 2026,
            "mes": 4,
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
        assert existing_exportacao.ano == update_data["ano"]
        assert existing_exportacao.mes == update_data["mes"]
        assert existing_exportacao.peso == update_data["peso"]
        assert existing_exportacao.valor == update_data["valor"]

    def test_update_different_codigo(self, client, existing_exportacao, session):
        """Test Update an existing entry with different codigo is successful."""
        dependencies = create_exportacao_dependencies(session)
        update_data = {
            "ano": 2026,
            "mes": 4,
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
        assert existing_exportacao.ano == update_data["ano"]
        assert existing_exportacao.mes == update_data["mes"]

    def test_update_nonexistent(self, client, session):
        """Test updating non-existent Exportacao"""
        dependencies = create_exportacao_dependencies(session)
        exportacao_data = make_exportacao_data(dependencies)
        response = client.put(f"{url}9999", json=exportacao_data)

        assert response.status_code == 404
        assert "Nenhum registro encontrado" in response.json["message"]

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
