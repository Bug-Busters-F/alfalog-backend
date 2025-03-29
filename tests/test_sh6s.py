import pytest
from src.sh6s.model import SH6Model
from faker import Faker

url = "/api/sh6s/"
fake = Faker("pt_BR")


def make_sh6_data():
    return {
        "codigo": fake.unique.bothify(text="######"),
        "nome": fake.sentence(nb_words=6, variable_nb_words=True),
    }


def create_sh6_db(session, data=None) -> SH6Model:
    """Create test SH6 record"""
    data = data or make_sh6_data()
    sh6 = SH6Model(**data)
    session.add(sh6)
    session.commit()
    return sh6


class TestSH6Collection:
    def test_get_empty(self, client):
        """Test retrieving all entries when database is empty"""
        response = client.get(url)
        assert response.status_code == 200
        assert response.json == []

    def test_list_with_data(self, client, session):
        """Test retrieving all entries when database has data"""
        created_sh6 = create_sh6_db(session)

        response = client.get(url)
        assert response.status_code == 200
        assert isinstance(response.json, list)
        assert len(response.json) > 0

        listed_sh6 = response.json[0]["data"]
        assert listed_sh6["id"] == created_sh6.id
        assert listed_sh6["nome"] == created_sh6.nome

    def test_create_valid(self, client, session):
        """Test creating a valid SH6"""
        sh6_data = make_sh6_data()
        response = client.post(url, json=sh6_data)

        assert response.status_code == 201
        assert response.json["data"]["nome"] == sh6_data["nome"]
        assert response.json["data"]["codigo"] == sh6_data["codigo"]
        assert isinstance(response.json["data"]["id"], int)

        # Verify database
        db_sh6 = (
            session.query(SH6Model).filter_by(id=response.json["data"]["id"]).first()
        )
        assert db_sh6 is not None
        assert db_sh6.codigo == sh6_data["codigo"]

    def test_create_duplicate(self, client, session):
        """Test creating duplicate SH6 fails"""
        sh6_data = make_sh6_data()
        create_sh6_db(session, sh6_data)
        response = client.post(url, json=sh6_data)

        assert response.status_code == 422
        assert "Já existe um SH6 com esse código" in response.json["message"]

    @pytest.mark.parametrize(
        "payload, missing_field",
        [
            ({"codigo": "123456"}, "nome"),
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


class TestSH6Resource:
    """Tests for single SH6 resource endpoints (/api/sh6s/<id>)"""

    @pytest.fixture
    def existing_sh6(self, session) -> SH6Model:
        """Fixture providing an existing SH6"""
        return create_sh6_db(session)

    def test_get_existing(self, client, existing_sh6):
        """Test getting an existing SH6"""
        response = client.get(f"{url}{existing_sh6.id}")

        assert response.status_code == 200
        assert response.json["data"]["id"] == existing_sh6.id
        assert response.json["data"]["nome"] == existing_sh6.nome
        assert response.json["data"]["codigo"] == existing_sh6.codigo

    def test_get_nonexistent(self, client):
        """Test getting non-existent SH6"""
        response = client.get(f"{url}9999")
        assert response.status_code == 404
        assert "Nenhum registro encontrado" in response.json["message"]

    def test_update_same_codigo(self, client, existing_sh6, session):
        """Test updating with same codigo"""
        update_data = {
            "codigo": existing_sh6.codigo,
            "nome": "Produtos químicos atualizados",
        }
        response = client.put(f"{url}{existing_sh6.id}", json=update_data)
        assert response.status_code == 204

        # Verify update
        session.refresh(existing_sh6)
        assert existing_sh6.codigo == update_data["codigo"]
        assert existing_sh6.nome == update_data["nome"]

    def test_update_different_codigo(self, client, existing_sh6, session):
        """Test updating with different codigo"""
        update_data = {"codigo": "654321", "nome": "Produtos químicos modificados"}
        response = client.put(f"{url}{existing_sh6.id}", json=update_data)
        assert response.status_code == 204

        # Verify update
        session.refresh(existing_sh6)
        assert existing_sh6.codigo == update_data["codigo"]
        assert existing_sh6.nome == update_data["nome"]

    def test_update_nonexistent(self, client):
        """Test updating non-existent SH6"""
        response = client.put(f"{url}9999", json=make_sh6_data())
        assert response.status_code == 404
        assert "Nenhum registro encontrado" in response.json["message"]

    def test_update_existent_codigo(self, client, existing_sh6, session):
        """Test updating with existing codigo fails"""
        data = {"codigo": "111111", "nome": "Outros produtos químicos específicos"}
        sh6_2 = create_sh6_db(session, data)

        data["codigo"] = existing_sh6.codigo
        response = client.put(f"{url}{sh6_2.id}", json=data)

        assert response.status_code == 422
        assert "Já existe um SH6 com esse código" in response.json["message"]

    def test_delete_existing(self, client, existing_sh6, session):
        """Test deleting existing SH6"""
        response = client.delete(f"{url}{existing_sh6.id}")
        assert response.status_code == 204

        # Verify deletion
        assert session.get(SH6Model, existing_sh6.id) is None

    def test_delete_nonexistent(self, client):
        """Test deleting non-existent SH6"""
        response = client.delete(f"{url}9999")
        assert response.status_code == 404
        assert "Nenhum registro encontrado" in response.json["message"]
