import pytest
from src.vias.model import ViaModel
from faker import Faker

url = "/api/vias/"
fake = Faker("pt_BR")


def make_via_data():
    return {
        "codigo": fake.unique.bothify(text="####"),
        "nome": "Via " + fake.unique.street_name(),
    }


def create_via_db(session, data=None) -> ViaModel:
    """Create test Via record"""
    data = data or make_via_data()
    via = ViaModel(**data)
    session.add(via)
    session.commit()
    return via


class TestViaCollection:
    def test_get_empty(self, client):
        """Test Retrieve all entries when database is empty is successful."""
        response = client.get(url)
        assert response.status_code == 200
        assert response.json == []

    def test_list_with_data(self, client, session):
        """Test Retrieve all entries when database has data is successful."""
        created_via = create_via_db(session)

        response = client.get(url)
        assert response.status_code == 200

        assert isinstance(response.json, list)
        assert len(response.json) > 0

        listed_via = response.json[0]["data"]
        assert listed_via["id"] == created_via.id
        assert listed_via["nome"] == created_via.nome

    def test_create_valid(self, client, session):
        """Test creating a valid Via"""
        via_data = make_via_data()
        response = client.post(url, json=via_data)

        assert response.status_code == 201
        assert response.json["data"]["nome"] == via_data["nome"]
        assert response.json["data"]["codigo"] == via_data["codigo"]
        assert isinstance(response.json["data"]["id"], int)

        # Verify database
        db_via = (
            session.query(ViaModel).filter_by(id=response.json["data"]["id"]).first()
        )
        assert db_via is not None
        assert db_via.codigo == via_data["codigo"]

    def test_create_duplicate(self, client, session):
        """Test Create an entry with an existing codigo fails."""
        via_data = make_via_data()
        create_via_db(session, via_data)
        response = client.post(url, json=via_data)

        assert response.status_code == 422
        assert "Já existe uma Via com esse código" in response.json["message"]

    @pytest.mark.parametrize(
        "payload, missing_field",
        [
            ({"codigo": "1234"}, "nome"),
            ({"nome": "Via Test"}, "codigo"),
            ({}, "nome"),
        ],
    )
    def test_create_missing_fields(self, client, payload, missing_field, session):
        """Test validation for missing required fields"""
        response = client.post(url, json=payload)

        assert response.status_code == 400
        assert "message" in response.json
        assert missing_field in response.json["message"]


class TestViaResource:
    """Tests for single Via resource endpoints (/api/vias/<id>)"""

    @pytest.fixture
    def existing_via(self, session) -> ViaModel:
        """Fixture providing an existing Via."""
        return create_via_db(session)

    def test_get_existing(self, client, existing_via):
        """Test getting an existing Via."""
        response = client.get(f"{url}{existing_via.id}")

        assert response.status_code == 200
        assert response.json["data"]["id"] == existing_via.id
        assert response.json["data"]["nome"] == existing_via.nome
        assert response.json["data"]["codigo"] == existing_via.codigo

    def test_get_nonexistent(self, client):
        """Test getting non-existent Via."""
        response = client.get(f"{url}9999")
        assert response.status_code == 404
        assert "Nenhum registro encontrado" in response.json["message"]

    def test_update_same_codigo(self, client, existing_via, session):
        """Test Update an existing entry with a different codigo is successful."""
        update_data = {
            "nome": "Updated Via",
            "codigo": existing_via.codigo,
        }
        response = client.put(f"{url}{existing_via.id}", json=update_data)
        assert response.status_code == 204

        # Verify update
        session.refresh(existing_via)
        assert existing_via.nome == update_data["nome"]
        assert existing_via.codigo == update_data["codigo"]

    def test_update_different_codigo(self, client, existing_via, session):
        """Test Update an existing entry with a different codigo is successful."""
        update_data = {
            "nome": "Updated Via",
            "codigo": "5678",
        }
        response = client.put(f"{url}{existing_via.id}", json=update_data)
        assert response.status_code == 204

        # Verify update
        session.refresh(existing_via)
        assert existing_via.nome == update_data["nome"]
        assert existing_via.codigo == update_data["codigo"]

    def test_update_nonexistent(self, client):
        """Test updating non-existent Via"""
        response = client.put(f"{url}9999", json=make_via_data())
        assert response.status_code == 404
        assert "Nenhum registro encontrado" in response.json["message"]

    def test_update_existent_codigo(self, client, existing_via, session):
        """Test updating with an existent codigo fails."""
        data = {
            "nome": "Via Test 2",
            "codigo": "4321",
        }
        via2 = create_via_db(session, data)

        data["codigo"] = existing_via.codigo
        response = client.put(f"{url}{via2.id}", json=data)

        assert response.status_code == 422
        assert "Já existe uma Via com esse código" in response.json["message"]

    def test_delete_existing(self, client, existing_via, session):
        """Test deleting existing Via"""
        response = client.delete(f"{url}{existing_via.id}")

        assert response.status_code == 204

        # Verify deletion
        assert session.get(ViaModel, existing_via.id) is None

    def test_delete_nonexistent(self, client):
        """Test deleting non-existent Via"""
        response = client.delete(f"{url}9999")

        assert response.status_code == 404
        assert "Nenhum registro encontrado" in response.json["message"]
