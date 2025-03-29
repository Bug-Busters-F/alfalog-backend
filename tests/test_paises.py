import pytest
from faker import Faker
from src.paises.model import PaisModel

url = "/api/paises/"
fake = Faker("pt_BR")


def make_pais_data():
    return {
        "codigo": fake.unique.bothify(text="####"),
        "nome": fake.unique.country(),
    }


def create_pais_db(session, data=None) -> PaisModel:
    """Create test Pais record"""
    data = data or make_pais_data()
    pais = PaisModel(**data)
    session.add(pais)
    session.commit()
    return pais


class TestPaisCollection:
    def test_get_empty(self, client):
        """Test retrieving all entries when database is empty"""
        response = client.get(url)
        assert response.status_code == 200
        assert response.json == []

    def test_list_with_data(self, client, session):
        """Test retrieving all entries when database has data"""
        created_pais = create_pais_db(session)

        response = client.get(url)
        assert response.status_code == 200
        assert isinstance(response.json, list)
        assert len(response.json) > 0

        listed_pais = response.json[0]["data"]
        assert listed_pais["id"] == created_pais.id
        assert listed_pais["nome"] == created_pais.nome

    def test_create_valid(self, client, session):
        """Test creating a valid Pais"""
        pais_data = make_pais_data()
        response = client.post(url, json=pais_data)

        assert response.status_code == 201
        assert response.json["data"]["nome"] == pais_data["nome"]
        assert response.json["data"]["codigo"] == pais_data["codigo"]
        assert isinstance(response.json["data"]["id"], int)

        # Verify database
        db_pais = (
            session.query(PaisModel).filter_by(id=response.json["data"]["id"]).first()
        )
        assert db_pais is not None
        assert db_pais.codigo == pais_data["codigo"]

    def test_create_duplicate(self, client, session):
        """Test creating duplicate Pais fails"""
        pais_data = make_pais_data()
        create_pais_db(session, pais_data)
        response = client.post(url, json=pais_data)

        assert response.status_code == 422
        assert "Já existe um País com esse código" in response.json["message"]

    @pytest.mark.parametrize(
        "payload, missing_field",
        [
            ({"codigo": "1058"}, "nome"),
            ({"nome": "Brasil"}, "codigo"),
            ({}, "nome"),
        ],
    )
    def test_create_missing_fields(self, client, payload, missing_field, session):
        """Test validation for missing required fields"""
        response = client.post(url, json=payload)

        assert response.status_code == 400
        assert "message" in response.json
        assert missing_field in response.json["message"]


class TestPaisResource:
    """Tests for single Pais resource endpoints (/api/paises/<id>)"""

    @pytest.fixture
    def existing_pais(self, session) -> PaisModel:
        """Fixture providing an existing Pais"""
        return create_pais_db(session)

    def test_get_existing(self, client, existing_pais):
        """Test getting an existing Pais"""
        response = client.get(f"{url}{existing_pais.id}")

        assert response.status_code == 200
        assert response.json["data"]["id"] == existing_pais.id
        assert response.json["data"]["nome"] == existing_pais.nome
        assert response.json["data"]["codigo"] == existing_pais.codigo

    def test_get_nonexistent(self, client):
        """Test getting non-existent Pais"""
        response = client.get(f"{url}9999")
        assert response.status_code == 404
        assert "Nenhum registro encontrado" in response.json["message"]

    def test_update_same_codigo(self, client, existing_pais, session):
        """Test updating with same codigo"""
        update_data = {"codigo": existing_pais.codigo, "nome": "Brasil Atualizado"}
        response = client.put(f"{url}{existing_pais.id}", json=update_data)
        assert response.status_code == 204

        # Verify update
        session.refresh(existing_pais)
        assert existing_pais.codigo == update_data["codigo"]
        assert existing_pais.nome == update_data["nome"]

    def test_update_different_codigo(self, client, existing_pais, session):
        """Test updating with different codigo"""
        update_data = {"codigo": "9999", "nome": "Brasil Modificado"}
        response = client.put(f"{url}{existing_pais.id}", json=update_data)
        assert response.status_code == 204

        # Verify update
        session.refresh(existing_pais)
        assert existing_pais.codigo == update_data["codigo"]
        assert existing_pais.nome == update_data["nome"]

    def test_update_nonexistent(self, client):
        """Test updating non-existent Pais"""
        response = client.put(f"{url}9999", json=make_pais_data())
        assert response.status_code == 404
        assert "Nenhum registro encontrado" in response.json["message"]

    def test_update_existent_codigo(self, client, existing_pais, session):
        """Test updating with existing codigo fails"""
        data = {"codigo": "1111", "nome": "Argentina"}
        pais2 = create_pais_db(session, data)

        data["codigo"] = existing_pais.codigo
        response = client.put(f"{url}{pais2.id}", json=data)

        assert response.status_code == 422
        assert "Já existe um País com esse código" in response.json["message"]

    def test_delete_existing(self, client, existing_pais, session):
        """Test deleting existing Pais"""
        response = client.delete(f"{url}{existing_pais.id}")
        assert response.status_code == 204

        # Verify deletion
        assert session.get(PaisModel, existing_pais.id) is None

    def test_delete_nonexistent(self, client):
        """Test deleting non-existent Pais"""
        response = client.delete(f"{url}9999")
        assert response.status_code == 404
        assert "Nenhum registro encontrado" in response.json["message"]
