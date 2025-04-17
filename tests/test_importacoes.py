import pytest
from faker import Faker
from src.importacoes.model import ImportacaoModel
from tests.test_ncms import create_ncm_db
from tests.test_ues import create_ue_db
from tests.test_paises import create_pais_db
from tests.test_ufs import create_uf_db
from tests.test_vias import create_via_db
from tests.test_urfs import create_urf_db

url = "/api/importacoes/"
fake = Faker("pt_BR")


def make_importacao_data(dependencies):
    """Create test Importacao data with dependencies"""
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


def create_importacao_dependencies(session):
    """Create all dependencies for Importacao in database"""
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


def create_importacao_db(session, data=None, dependencies=None) -> ImportacaoModel:
    """Create test Importacao record with all dependencies"""
    dependencies = dependencies or create_importacao_dependencies(session)
    importacao_data = data or make_importacao_data(dependencies)

    importacao = ImportacaoModel(**importacao_data)
    session.add(importacao)
    session.commit()
    return importacao


class TestImportacaoCollection:
    def test_get_empty(self, client):
        """Test Retrieve all entries when database is empty is successful."""
        response = client.get(url)
        assert response.status_code == 200
        assert response.json == []

    def test_list_with_data(self, client, session):
        """Test Retrieve all entries when database has data is successful."""
        created_importacao = create_importacao_db(session)

        response = client.get(url)
        assert response.status_code == 200
        assert isinstance(response.json, list)
        assert len(response.json) > 0

        listed_importacao = response.json[0]["data"]
        assert listed_importacao["id"] == created_importacao.id
        assert listed_importacao["nome"] == created_importacao.nome

    def test_create_valid(self, client, session):
        """Test creating a valid Importacao"""
        dependencies = create_importacao_dependencies(session)
        importacao_data = make_importacao_data(dependencies)

        response = client.post(url, json=importacao_data)

        assert response.status_code == 201
        assert response.json["data"]["nome"] == importacao_data["nome"]
        assert response.json["data"]["codigo"] == importacao_data["codigo"]
        assert response.json["data"]["ano"] == importacao_data["ano"]
        assert response.json["data"]["mes"] == importacao_data["mes"]
        assert response.json["data"]["quantidade"] == importacao_data["quantidade"]
        assert response.json["data"]["peso"] == importacao_data["peso"]
        assert response.json["data"]["valor"] == importacao_data["valor"]
        assert isinstance(response.json["data"]["id"], int)

        # Verify database
        db_importacao = (
            session.query(ImportacaoModel)
            .filter_by(id=response.json["data"]["id"])
            .first()
        )
        assert db_importacao is not None
        assert db_importacao.codigo == importacao_data["codigo"]

    def test_create_duplicate(self, client, session):
        """Test Create an entry with an existing codigo fails."""
        importacao_data = make_importacao_data(create_importacao_dependencies(session))
        create_importacao_db(session, importacao_data)
        response = client.post(url, json=importacao_data)

        assert response.status_code == 422
        assert "Já existe uma Importacao com esse código" in response.json["message"]

    @pytest.mark.parametrize(
        "payload, missing_field",
        [
            ({"codigo": "1234"}, "nome"),
            ({"nome": "Importacao Test"}, "codigo"),
            ({}, "nome"),
        ],
    )
    def test_create_missing_fields(self, client, payload, missing_field, session):
        """Test validation for missing required fields"""
        dependencies = create_importacao_dependencies(session)
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


class TestImportacaoResource:
    """Tests for single Importacao resource endpoints (/api/importacoes/<id>)"""

    @pytest.fixture
    def existing_importacao(self, session) -> ImportacaoModel:
        """Fixture providing an existing Importacao."""
        return create_importacao_db(session)

    def test_get_existing(self, client, existing_importacao):
        """Test getting an existing Importacao."""
        response = client.get(f"{url}{existing_importacao.id}")

        assert response.status_code == 200
        assert response.json["data"]["id"] == existing_importacao.id
        assert response.json["data"]["nome"] == existing_importacao.nome
        assert response.json["data"]["codigo"] == existing_importacao.codigo
        assert response.json["data"]["ano"] == existing_importacao.ano
        assert response.json["data"]["mes"] == existing_importacao.mes
        assert response.json["data"]["quantidade"] == existing_importacao.quantidade
        assert response.json["data"]["peso"] == existing_importacao.peso
        assert response.json["data"]["valor"] == existing_importacao.valor

    def test_get_nonexistent(self, client):
        """Test getting non-existent Importacao."""
        response = client.get(f"{url}9999")
        assert response.status_code == 404
        assert "Nenhum registro encontrado" in response.json["message"]

    def test_update_same_codigo(self, client, existing_importacao, session):
        """Test Update an existing entry with same codigo is successful."""
        dependencies = create_importacao_dependencies(session)
        update_data = {
            "nome": "Updated Importacao",
            "codigo": existing_importacao.codigo,
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
        response = client.put(f"{url}{existing_importacao.id}", json=update_data)
        assert response.status_code == 204

        # Verify update
        session.refresh(existing_importacao)
        assert existing_importacao.nome == update_data["nome"]
        assert existing_importacao.codigo == update_data["codigo"]
        assert existing_importacao.ano == update_data["ano"]
        assert existing_importacao.mes == update_data["mes"]
        assert existing_importacao.quantidade == update_data["quantidade"]
        assert existing_importacao.peso == update_data["peso"]
        assert existing_importacao.valor == update_data["valor"]

    def test_update_different_codigo(self, client, existing_importacao, session):
        """Test Update an existing entry with different codigo is successful."""
        dependencies = create_importacao_dependencies(session)
        update_data = {
            "nome": "Updated Importacao",
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
        response = client.put(f"{url}{existing_importacao.id}", json=update_data)
        assert response.status_code == 204

        # Verify update
        session.refresh(existing_importacao)
        assert existing_importacao.nome == update_data["nome"]
        assert existing_importacao.codigo == update_data["codigo"]

    def test_update_nonexistent(self, client, session):
        """Test updating non-existent Importacao"""
        dependencies = create_importacao_dependencies(session)
        importacao_data = make_importacao_data(dependencies)
        response = client.put(f"{url}9999", json=importacao_data)

        assert response.status_code == 404
        assert "Nenhum registro encontrado" in response.json["message"]

    def test_update_existent_codigo(self, client, existing_importacao, session):
        """Test updating with an existent codigo fails."""
        data = make_importacao_data(create_importacao_dependencies(session))
        importacao2 = create_importacao_db(session, data)

        data["codigo"] = existing_importacao.codigo
        response = client.put(f"{url}{importacao2.id}", json=data)

        assert response.status_code == 422
        assert "Já existe uma Importacao com esse código" in response.json["message"]

    def test_delete_existing(self, client, existing_importacao, session):
        """Test deleting existing Importacao"""
        response = client.delete(f"{url}{existing_importacao.id}")

        assert response.status_code == 204

        # Verify deletion
        assert session.get(ImportacaoModel, existing_importacao.id) is None

    def test_delete_nonexistent(self, client):
        """Test deleting non-existent Importacao"""
        response = client.delete(f"{url}9999")

        assert response.status_code == 404
        assert "Nenhum registro encontrado" in response.json["message"]
