import pytest
from src.ncms.model import NCMModel
from faker import Faker

url = "/api/ncms/"
fake = Faker("pt_BR")


def make_ncm_data():
    return {
        "codigo": fake.unique.bothify(text="########"),
        "descricao": fake.sentence(nb_words=5, variable_nb_words=True),
    }


def create_ncm_db(session, data=None) -> NCMModel:
    """Create test NCM record"""
    data = data or make_ncm_data()
    ncm = NCMModel(**data)
    session.add(ncm)
    session.commit()
    return ncm


class TestNCMCollection:
    def test_get_empty(self, client):
        """Test retrieving all entries when database is empty"""
        response = client.get(url)
        assert response.status_code == 200
        assert response.json == []

    def test_list_with_data(self, client, session):
        """Test retrieving all entries when database has data"""
        created_ncm = create_ncm_db(session)

        response = client.get(url)
        assert response.status_code == 200
        assert isinstance(response.json, list)
        assert len(response.json) > 0

        listed_ncm = response.json[0]["data"]
        assert listed_ncm["id"] == created_ncm.id
        assert listed_ncm["descricao"] == created_ncm.descricao

    def test_create_valid(self, client, session):
        """Test creating a valid NCM"""
        ncm_data = make_ncm_data()
        response = client.post(url, json=ncm_data)

        assert response.status_code == 201
        assert response.json["data"]["codigo"] == ncm_data["codigo"]
        assert response.json["data"]["descricao"] == ncm_data["descricao"]
        assert isinstance(response.json["data"]["id"], int)

        # Verify database
        db_ncm = (
            session.query(NCMModel).filter_by(id=response.json["data"]["id"]).first()
        )
        assert db_ncm is not None
        assert db_ncm.codigo == ncm_data["codigo"]

    def test_create_duplicate(self, client, session):
        """Test creating duplicate NCM fails"""
        ncm_data = make_ncm_data()
        create_ncm_db(session, ncm_data)
        response = client.post(url, json=ncm_data)

        assert response.status_code == 422
        assert "Já existe um NCM com esse código" in response.json["message"]

    @pytest.mark.parametrize(
        "payload, missing_field",
        [
            ({"codigo": "12345678"}, "descricao"),
            ({"descricao": "Descrição Teste"}, "codigo"),
            ({}, "codigo"),
        ],
    )
    def test_create_missing_fields(self, client, payload, missing_field, session):
        """Test validation for missing required fields"""
        response = client.post(url, json=payload)

        assert response.status_code == 400
        assert "message" in response.json
        assert missing_field in response.json["message"]


class TestNCMResource:
    """Tests for single NCM resource endpoints (/api/ncms/<id>)"""

    @pytest.fixture
    def existing_ncm(self, session) -> NCMModel:
        """Fixture providing an existing NCM"""
        return create_ncm_db(session)

    def test_get_existing(self, client, existing_ncm):
        """Test getting an existing NCM"""
        response = client.get(f"{url}{existing_ncm.id}")

        assert response.status_code == 200
        assert response.json["data"]["id"] == existing_ncm.id
        assert response.json["data"]["codigo"] == existing_ncm.codigo
        assert response.json["data"]["descricao"] == existing_ncm.descricao

    def test_get_nonexistent(self, client):
        """Test getting non-existent NCM"""
        response = client.get(f"{url}9999")
        assert response.status_code == 404
        assert "Nenhum registro encontrado" in response.json["message"]

    def test_update_same_codigo(self, client, existing_ncm, session):
        """Test updating with same codigo"""
        update_data = {
            "codigo": existing_ncm.codigo,
            "descricao": "Descrição Atualizada",
        }
        response = client.put(f"{url}{existing_ncm.id}", json=update_data)
        assert response.status_code == 204

        # Verify update
        session.refresh(existing_ncm)
        assert existing_ncm.codigo == update_data["codigo"]
        assert existing_ncm.descricao == update_data["descricao"]

    def test_update_different_codigo(self, client, existing_ncm, session):
        """Test updating with different codigo"""
        update_data = {
            "codigo": "87654321",
            "descricao": "Descrição Atualizada",
        }
        response = client.put(f"{url}{existing_ncm.id}", json=update_data)
        assert response.status_code == 204

        # Verify update
        session.refresh(existing_ncm)
        assert existing_ncm.codigo == update_data["codigo"]
        assert existing_ncm.descricao == update_data["descricao"]

    def test_update_nonexistent(self, client):
        """Test updating non-existent NCM"""
        response = client.put(f"{url}9999", json=make_ncm_data())
        assert response.status_code == 404
        assert "Nenhum registro encontrado" in response.json["message"]

    def test_update_existent_codigo(self, client, existing_ncm, session):
        """Test updating with existing codigo fails"""
        data = {
            "codigo": "11112222",
            "descricao": "Outro NCM",
        }
        ncm2 = create_ncm_db(session, data)

        data["codigo"] = existing_ncm.codigo
        response = client.put(f"{url}{ncm2.id}", json=data)

        assert response.status_code == 422
        assert "Já existe um NCM com esse código" in response.json["message"]

    def test_delete_existing(self, client, existing_ncm, session):
        """Test deleting existing NCM"""
        response = client.delete(f"{url}{existing_ncm.id}")
        assert response.status_code == 204

        # Verify deletion
        assert session.get(NCMModel, existing_ncm.id) is None

    def test_delete_nonexistent(self, client):
        """Test deleting non-existent NCM"""
        response = client.delete(f"{url}9999")

        assert response.status_code == 404
        assert "Nenhum registro encontrado" in response.json["message"]
