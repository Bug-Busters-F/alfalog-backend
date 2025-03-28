import pytest
from faker import Faker
from src.sh4s.model import SH4Model

url = "/api/sh4s/"
fake = Faker("pt_BR")


def make_sh4_data():
    return {
        "codigo": fake.unique.bothify(text="####"),
        "nome": fake.sentence(nb_words=4, variable_nb_words=True),
    }


def create_sh4_db(session, data=None) -> SH4Model:
    """Create test SH4 record"""
    data = data or make_sh4_data()
    sh4 = SH4Model(**data)
    session.add(sh4)
    session.commit()
    return sh4


class TestSH4Collection:
    def test_get_empty(self, client):
        """Test retrieving all entries when database is empty"""
        response = client.get(url)
        assert response.status_code == 200
        assert response.json == []

    def test_list_with_data(self, client, session):
        """Test retrieving all entries when database has data"""
        created_sh4 = create_sh4_db(session)

        response = client.get(url)
        assert response.status_code == 200
        assert isinstance(response.json, list)
        assert len(response.json) > 0

        listed_sh4 = response.json[0]["data"]
        assert listed_sh4["id"] == created_sh4.id
        assert listed_sh4["nome"] == created_sh4.nome

    def test_create_valid(self, client, session):
        """Test creating a valid SH4"""
        sh4_data = make_sh4_data()
        response = client.post(url, json=sh4_data)

        assert response.status_code == 201
        assert response.json["data"]["nome"] == sh4_data["nome"]
        assert response.json["data"]["codigo"] == sh4_data["codigo"]
        assert isinstance(response.json["data"]["id"], int)

        # Verify database
        db_sh4 = (
            session.query(SH4Model).filter_by(id=response.json["data"]["id"]).first()
        )
        assert db_sh4 is not None
        assert db_sh4.codigo == sh4_data["codigo"]

    def test_create_duplicate(self, client, session):
        """Test creating duplicate SH4 fails"""
        sh4_data = make_sh4_data()
        create_sh4_db(session, sh4_data)
        response = client.post(url, json=sh4_data)

        assert response.status_code == 422
        assert "Já existe um SH4 com esse código" in response.json["message"]

    @pytest.mark.parametrize(
        "payload, missing_field",
        [
            ({"codigo": "1234"}, "nome"),
            ({"nome": "Produtos químicos"}, "codigo"),
            ({}, "nome"),
        ],
    )
    def test_create_missing_fields(self, client, payload, missing_field, session):
        """Test validation for missing required fields"""
        response = client.post(url, json=payload)

        assert response.status_code == 400
        assert "message" in response.json
        assert missing_field in response.json["message"]


class TestSH4Resource:
    """Tests for single SH4 resource endpoints (/api/sh4s/<id>)"""

    @pytest.fixture
    def existing_sh4(self, session) -> SH4Model:
        """Fixture providing an existing SH4"""
        return create_sh4_db(session)

    def test_get_existing(self, client, existing_sh4):
        """Test getting an existing SH4"""
        response = client.get(f"{url}{existing_sh4.id}")

        assert response.status_code == 200
        assert response.json["data"]["id"] == existing_sh4.id
        assert response.json["data"]["nome"] == existing_sh4.nome
        assert response.json["data"]["codigo"] == existing_sh4.codigo

    def test_get_nonexistent(self, client):
        """Test getting non-existent SH4"""
        response = client.get(f"{url}9999")
        assert response.status_code == 404
        assert "Nenhum registro encontrado" in response.json["message"]

    def test_update_same_codigo(self, client, existing_sh4, session):
        """Test updating with same codigo"""
        update_data = {
            "codigo": existing_sh4.codigo,
            "nome": "Produtos químicos atualizados",
        }
        response = client.put(f"{url}{existing_sh4.id}", json=update_data)
        assert response.status_code == 204

        # Verify update
        session.refresh(existing_sh4)
        assert existing_sh4.codigo == update_data["codigo"]
        assert existing_sh4.nome == update_data["nome"]

    def test_update_different_codigo(self, client, existing_sh4, session):
        """Test updating with different codigo"""
        update_data = {"codigo": "5678", "nome": "Produtos químicos modificados"}
        response = client.put(f"{url}{existing_sh4.id}", json=update_data)
        assert response.status_code == 204

        # Verify update
        session.refresh(existing_sh4)
        assert existing_sh4.codigo == update_data["codigo"]
        assert existing_sh4.nome == update_data["nome"]

    def test_update_nonexistent(self, client):
        """Test updating non-existent SH4"""
        response = client.put(f"{url}9999", json=make_sh4_data())
        assert response.status_code == 404
        assert "Nenhum registro encontrado" in response.json["message"]

    def test_update_existent_codigo(self, client, existing_sh4, session):
        """Test updating with existing codigo fails"""
        data = {"codigo": "1111", "nome": "Outros produtos químicos"}
        sh4_2 = create_sh4_db(session, data)

        data["codigo"] = existing_sh4.codigo
        response = client.put(f"{url}{sh4_2.id}", json=data)

        assert response.status_code == 422
        assert "Já existe um SH4 com esse código" in response.json["message"]

    def test_delete_existing(self, client, existing_sh4, session):
        """Test deleting existing SH4"""
        response = client.delete(f"{url}{existing_sh4.id}")
        assert response.status_code == 204

        # Verify deletion
        assert session.get(SH4Model, existing_sh4.id) is None

    def test_delete_nonexistent(self, client):
        """Test deleting non-existent SH4"""
        response = client.delete(f"{url}9999")
        assert response.status_code == 404
        assert "Nenhum registro encontrado" in response.json["message"]
