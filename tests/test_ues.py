import pytest
from src.ues.model import UEModel
from faker import Faker

url = "/api/ues/"
fake = Faker("pt_BR")


def make_ue_data():
    return {
        "codigo": fake.unique.bothify(text="####"),
        "nome": fake.unique.word().capitalize(),
        "abreviacao": fake.unique.bothify(text="???").upper(),
    }


def create_ue_db(session, data=None) -> UEModel:
    """Create test UE record"""
    data = data or make_ue_data()
    ue = UEModel(**data)
    session.add(ue)
    session.commit()
    return ue


class TestUECollection:
    def test_get_empty(self, client):
        """Test retrieving all entries when database is empty"""
        response = client.get(url)
        assert response.status_code == 200
        assert response.json == []

    def test_list_with_data(self, client, session):
        """Test retrieving all entries when database has data"""
        created_ue = create_ue_db(session)

        response = client.get(url)
        assert response.status_code == 200
        assert isinstance(response.json, list)
        assert len(response.json) > 0

        listed_ue = response.json[0]["data"]
        assert listed_ue["id"] == created_ue.id
        assert listed_ue["nome"] == created_ue.nome

    def test_create_valid(self, client, session):
        """Test creating a valid UE"""
        ue_data = make_ue_data()
        response = client.post(url, json=ue_data)

        assert response.status_code == 201
        assert response.json["data"]["nome"] == ue_data["nome"]
        assert response.json["data"]["codigo"] == ue_data["codigo"]
        assert response.json["data"]["abreviacao"] == ue_data["abreviacao"]
        assert isinstance(response.json["data"]["id"], int)

        # Verify database
        db_ue = session.query(UEModel).filter_by(id=response.json["data"]["id"]).first()
        assert db_ue is not None
        assert db_ue.codigo == ue_data["codigo"]

    def test_create_duplicate(self, client, session):
        """Test creating duplicate UE fails"""
        ue_data = make_ue_data()
        create_ue_db(session, ue_data)
        response = client.post(url, json=ue_data)

        assert response.status_code == 422
        assert "Já existe uma UE com esse código" in response.json["message"]

    @pytest.mark.parametrize(
        "payload, missing_field",
        [
            ({"codigo": "1234"}, "nome"),
            ({"nome": "Unidade Teste"}, "codigo"),
            ({"abreviacao": "UT"}, "nome"),
            ({}, "nome"),
        ],
    )
    def test_create_missing_fields(self, client, payload, missing_field, session):
        """Test validation for missing required fields"""
        response = client.post(url, json=payload)

        assert response.status_code == 400
        assert "message" in response.json
        assert missing_field in response.json["message"]


class TestUEResource:
    """Tests for single UE resource endpoints (/api/ues/<id>)"""

    @pytest.fixture
    def existing_ue(self, session) -> UEModel:
        """Fixture providing an existing UE"""
        return create_ue_db(session)

    def test_get_existing(self, client, existing_ue):
        """Test getting an existing UE"""
        response = client.get(f"{url}{existing_ue.id}")

        assert response.status_code == 200
        assert response.json["data"]["id"] == existing_ue.id
        assert response.json["data"]["nome"] == existing_ue.nome
        assert response.json["data"]["codigo"] == existing_ue.codigo
        assert response.json["data"]["abreviacao"] == existing_ue.abreviacao

    def test_get_nonexistent(self, client):
        """Test getting non-existent UE"""
        response = client.get(f"{url}9999")
        assert response.status_code == 404
        assert "Nenhum registro encontrado" in response.json["message"]

    def test_update_same_codigo(self, client, existing_ue, session):
        """Test updating with same codigo"""
        update_data = {
            "codigo": existing_ue.codigo,
            "nome": "Unidade Atualizada",
            "abreviacao": "UA",
        }
        response = client.put(f"{url}{existing_ue.id}", json=update_data)
        assert response.status_code == 204

        # Verify update
        session.refresh(existing_ue)
        assert existing_ue.codigo == update_data["codigo"]
        assert existing_ue.nome == update_data["nome"]
        assert existing_ue.abreviacao == update_data["abreviacao"]

    def test_update_different_codigo(self, client, existing_ue, session):
        """Test updating with different codigo"""
        update_data = {
            "codigo": "5678",
            "nome": "Unidade Modificada",
            "abreviacao": "UM",
        }
        response = client.put(f"{url}{existing_ue.id}", json=update_data)
        assert response.status_code == 204

        # Verify update
        session.refresh(existing_ue)
        assert existing_ue.codigo == update_data["codigo"]
        assert existing_ue.nome == update_data["nome"]
        assert existing_ue.abreviacao == update_data["abreviacao"]

    def test_update_nonexistent(self, client):
        """Test updating non-existent UE"""
        response = client.put(f"{url}9999", json=make_ue_data())
        assert response.status_code == 404
        assert "Nenhum registro encontrado" in response.json["message"]

    def test_update_existent_codigo(self, client, existing_ue, session):
        """Test updating with existing codigo fails"""
        data = {"codigo": "4321", "nome": "Outra Unidade", "abreviacao": "OU"}
        ue2 = create_ue_db(session, data)

        data["codigo"] = existing_ue.codigo
        response = client.put(f"{url}{ue2.id}", json=data)

        assert response.status_code == 422
        assert "Já existe uma UE com esse código" in response.json["message"]

    def test_delete_existing(self, client, existing_ue, session):
        """Test deleting existing UE"""
        response = client.delete(f"{url}{existing_ue.id}")
        assert response.status_code == 204

        # Verify deletion
        assert session.get(UEModel, existing_ue.id) is None

    def test_delete_nonexistent(self, client):
        """Test deleting non-existent UE"""
        response = client.delete(f"{url}9999")
        assert response.status_code == 404
        assert "Nenhum registro encontrado" in response.json["message"]
