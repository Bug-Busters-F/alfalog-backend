import pytest
from faker import Faker
from src.transacoes.model import TransacaoModel
from tests.test_ncms import create_ncm_db
from tests.test_ues import create_ue_db
from tests.test_paises import create_pais_db
from tests.test_ufs import create_uf_db
from tests.test_vias import create_via_db
from tests.test_urfs import create_urf_db

url = "/api/transacoes/"
fake = Faker("pt_BR")


def make_transacao_data(dependencies):
    """Create test Transacao data with dependencies"""
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


def create_transacao_dependencies(session):
    """Create all dependencies for Transacao in database"""
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


def create_transacao_db(session, data=None, dependencies=None) -> TransacaoModel:
    """Create test Transacao record with all dependencies"""
    dependencies = dependencies or create_transacao_dependencies(session)
    transacao_data = data or make_transacao_data(dependencies)

    transacao = TransacaoModel(**transacao_data)
    session.add(transacao)
    session.commit()
    return transacao


class TestTransacaoCollection:
    def test_get_empty(self, client):
        """Test Retrieve all entries when database is empty is successful."""
        response = client.get(url)
        assert response.status_code == 200
        assert response.json == []

    def test_list_with_data(self, client, session):
        """Test Retrieve all entries when database has data is successful."""
        created_transacao = create_transacao_db(session)

        response = client.get(url)
        assert response.status_code == 200
        assert isinstance(response.json, list)
        assert len(response.json) > 0

        listed_transacao = response.json[0]["data"]
        assert listed_transacao["id"] == created_transacao.id
        assert listed_transacao["nome"] == created_transacao.nome

    def test_create_valid(self, client, session):
        """Test creating a valid Transacao"""
        dependencies = create_transacao_dependencies(session)
        transacao_data = make_transacao_data(dependencies)

        response = client.post(url, json=transacao_data)

        assert response.status_code == 201
        assert response.json["data"]["nome"] == transacao_data["nome"]
        assert response.json["data"]["codigo"] == transacao_data["codigo"]
        assert response.json["data"]["ano"] == transacao_data["ano"]
        assert response.json["data"]["mes"] == transacao_data["mes"]
        assert response.json["data"]["quantidade"] == transacao_data["quantidade"]
        assert response.json["data"]["peso"] == transacao_data["peso"]
        assert response.json["data"]["valor"] == transacao_data["valor"]
        assert isinstance(response.json["data"]["id"], int)

        # Verify database
        db_transacao = (
            session.query(TransacaoModel)
            .filter_by(id=response.json["data"]["id"])
            .first()
        )
        assert db_transacao is not None
        assert db_transacao.codigo == transacao_data["codigo"]

    def test_create_duplicate(self, client, session):
        """Test Create an entry with an existing codigo fails."""
        transacao_data = make_transacao_data(create_transacao_dependencies(session))
        create_transacao_db(session, transacao_data)
        response = client.post(url, json=transacao_data)

        assert response.status_code == 422
        assert "Já existe uma Transacao com esse código" in response.json["message"]

    @pytest.mark.parametrize(
        "payload, missing_field",
        [
            ({"codigo": "1234"}, "nome"),
            ({"nome": "Transacao Test"}, "codigo"),
            ({}, "nome"),
        ],
    )
    def test_create_missing_fields(self, client, payload, missing_field, session):
        """Test validation for missing required fields"""
        dependencies = create_transacao_dependencies(session)
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


class TestTransacaoResource:
    """Tests for single Transacao resource endpoints (/api/transacoes/<id>)"""

    @pytest.fixture
    def existing_transacao(self, session) -> TransacaoModel:
        """Fixture providing an existing Transacao."""
        return create_transacao_db(session)

    def test_get_existing(self, client, existing_transacao):
        """Test getting an existing Transacao."""
        response = client.get(f"{url}{existing_transacao.id}")

        assert response.status_code == 200
        assert response.json["data"]["id"] == existing_transacao.id
        assert response.json["data"]["nome"] == existing_transacao.nome
        assert response.json["data"]["codigo"] == existing_transacao.codigo
        assert response.json["data"]["ano"] == existing_transacao.ano
        assert response.json["data"]["mes"] == existing_transacao.mes
        assert response.json["data"]["quantidade"] == existing_transacao.quantidade
        assert response.json["data"]["peso"] == existing_transacao.peso
        assert response.json["data"]["valor"] == existing_transacao.valor

    def test_get_nonexistent(self, client):
        """Test getting non-existent Transacao."""
        response = client.get(f"{url}9999")
        assert response.status_code == 404
        assert "Nenhum registro encontrado" in response.json["message"]

    def test_update_same_codigo(self, client, existing_transacao, session):
        """Test Update an existing entry with same codigo is successful."""
        dependencies = create_transacao_dependencies(session)
        update_data = {
            "nome": "Updated Transacao",
            "codigo": existing_transacao.codigo,
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
        response = client.put(f"{url}{existing_transacao.id}", json=update_data)
        assert response.status_code == 204

        # Verify update
        session.refresh(existing_transacao)
        assert existing_transacao.nome == update_data["nome"]
        assert existing_transacao.codigo == update_data["codigo"]
        assert existing_transacao.ano == update_data["ano"]
        assert existing_transacao.mes == update_data["mes"]
        assert existing_transacao.quantidade == update_data["quantidade"]
        assert existing_transacao.peso == update_data["peso"]
        assert existing_transacao.valor == update_data["valor"]

    def test_update_different_codigo(self, client, existing_transacao, session):
        """Test Update an existing entry with different codigo is successful."""
        dependencies = create_transacao_dependencies(session)
        update_data = {
            "nome": "Updated Transacao",
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
        response = client.put(f"{url}{existing_transacao.id}", json=update_data)
        assert response.status_code == 204

        # Verify update
        session.refresh(existing_transacao)
        assert existing_transacao.nome == update_data["nome"]
        assert existing_transacao.codigo == update_data["codigo"]

    def test_update_nonexistent(self, client, session):
        """Test updating non-existent Transacao"""
        dependencies = create_transacao_dependencies(session)
        transacao_data = make_transacao_data(dependencies)
        response = client.put(f"{url}9999", json=transacao_data)

        assert response.status_code == 404
        assert "Nenhum registro encontrado" in response.json["message"]

    def test_update_existent_codigo(self, client, existing_transacao, session):
        """Test updating with an existent codigo fails."""
        data = make_transacao_data(create_transacao_dependencies(session))
        transacao2 = create_transacao_db(session, data)

        data["codigo"] = existing_transacao.codigo
        response = client.put(f"{url}{transacao2.id}", json=data)

        assert response.status_code == 422
        assert "Já existe uma Transacao com esse código" in response.json["message"]

    def test_delete_existing(self, client, existing_transacao, session):
        """Test deleting existing Transacao"""
        response = client.delete(f"{url}{existing_transacao.id}")

        assert response.status_code == 204

        # Verify deletion
        assert session.get(TransacaoModel, existing_transacao.id) is None

    def test_delete_nonexistent(self, client):
        """Test deleting non-existent Transacao"""
        response = client.delete(f"{url}9999")

        assert response.status_code == 404
        assert "Nenhum registro encontrado" in response.json["message"]
