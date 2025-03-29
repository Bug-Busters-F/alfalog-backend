import pytest
from src.urfs.model import URFModel
from faker import Faker

url = "/api/urfs/"
fake = Faker("pt_BR")


def make_urf_data():
    return {
        "codigo": fake.unique.bothify(text="####"),
        "nome": "URF " + fake.unique.city(),
    }


def create_urf_db(session, data=None) -> URFModel:
    """Create test URF record"""
    data = data or make_urf_data()
    urf = URFModel(**data)
    session.add(urf)
    session.commit()
    return urf


class TestURFCollection:
    def test_get_empty(self, client):
        """Test retrieving all entries when database is empty"""
        response = client.get(url)
        assert response.status_code == 200
        assert response.json == []

    def test_list_with_data(self, client, session):
        """Test retrieving all entries when database has data"""
        created_urf = create_urf_db(session)

        response = client.get(url)
        assert response.status_code == 200
        assert isinstance(response.json, list)
        assert len(response.json) > 0

        listed_urf = response.json[0]["data"]
        assert listed_urf["id"] == created_urf.id
        assert listed_urf["nome"] == created_urf.nome

    def test_create_valid(self, client, session):
        """Test creating a valid URF"""
        urf_data = make_urf_data()
        response = client.post(url, json=urf_data)

        assert response.status_code == 201
        assert response.json["data"]["nome"] == urf_data["nome"]
        assert response.json["data"]["codigo"] == urf_data["codigo"]
        assert isinstance(response.json["data"]["id"], int)

        # Verify database
        db_urf = (
            session.query(URFModel).filter_by(id=response.json["data"]["id"]).first()
        )
        assert db_urf is not None
        assert db_urf.codigo == urf_data["codigo"]

    def test_create_duplicate(self, client, session):
        """Test creating duplicate URF fails"""
        urf_data = make_urf_data()
        create_urf_db(session, urf_data)
        response = client.post(url, json=urf_data)

        assert response.status_code == 422
        assert "Já existe uma URF com esse código" in response.json["message"]

    @pytest.mark.parametrize(
        "payload, missing_field",
        [
            ({"codigo": "1234"}, "nome"),
            ({"nome": "URF Teste"}, "codigo"),
            ({}, "nome"),
        ],
    )
    def test_create_missing_fields(self, client, payload, missing_field, session):
        """Test validation for missing required fields"""
        response = client.post(url, json=payload)

        assert response.status_code == 400
        assert "message" in response.json
        assert missing_field in response.json["message"]


class TestURFResource:
    """Tests for single URF resource endpoints (/api/urfs/<id>)"""

    @pytest.fixture
    def existing_urf(self, session) -> URFModel:
        """Fixture providing an existing URF"""
        return create_urf_db(session)

    def test_get_existing(self, client, existing_urf):
        """Test getting an existing URF"""
        response = client.get(f"{url}{existing_urf.id}")

        assert response.status_code == 200
        assert response.json["data"]["id"] == existing_urf.id
        assert response.json["data"]["nome"] == existing_urf.nome
        assert response.json["data"]["codigo"] == existing_urf.codigo

    def test_get_nonexistent(self, client):
        """Test getting non-existent URF"""
        response = client.get(f"{url}9999")
        assert response.status_code == 404
        assert "Nenhum registro encontrado" in response.json["message"]

    def test_update_same_codigo(self, client, existing_urf, session):
        """Test updating with same codigo"""
        update_data = {"codigo": existing_urf.codigo, "nome": "URF Atualizada"}
        response = client.put(f"{url}{existing_urf.id}", json=update_data)
        assert response.status_code == 204

        # Verify update
        session.refresh(existing_urf)
        assert existing_urf.codigo == update_data["codigo"]
        assert existing_urf.nome == update_data["nome"]

    def test_update_different_codigo(self, client, existing_urf, session):
        """Test updating with different codigo"""
        update_data = {"codigo": "5678", "nome": "URF Modificada"}
        response = client.put(f"{url}{existing_urf.id}", json=update_data)
        assert response.status_code == 204

        # Verify update
        session.refresh(existing_urf)
        assert existing_urf.codigo == update_data["codigo"]
        assert existing_urf.nome == update_data["nome"]

    def test_update_nonexistent(self, client):
        """Test updating non-existent URF"""
        response = client.put(f"{url}9999", json=make_urf_data())
        assert response.status_code == 404
        assert "Nenhum registro encontrado" in response.json["message"]

    def test_update_existent_codigo(self, client, existing_urf, session):
        """Test updating with existing codigo fails"""
        data = {"codigo": "1111", "nome": "Outra URF"}
        urf2 = create_urf_db(session, data)

        data["codigo"] = existing_urf.codigo
        response = client.put(f"{url}{urf2.id}", json=data)

        assert response.status_code == 422
        assert "Já existe uma URF com esse código" in response.json["message"]

    def test_delete_existing(self, client, existing_urf, session):
        """Test deleting existing URF"""
        response = client.delete(f"{url}{existing_urf.id}")
        assert response.status_code == 204

        # Verify deletion
        assert session.get(URFModel, existing_urf.id) is None

    def test_delete_nonexistent(self, client):
        """Test deleting non-existent URF"""
        response = client.delete(f"{url}9999")
        assert response.status_code == 404
        assert "Nenhum registro encontrado" in response.json["message"]
