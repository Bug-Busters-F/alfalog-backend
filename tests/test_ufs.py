import pytest
from faker import Faker
from src.ufs.model import UFModel

url = "/api/ufs/"
fake = Faker("pt_BR")


def make_uf_data():
    return {
        "nome": fake.state(),
        "codigo": fake.bothify(text="##"),
        "sigla": fake.bothify(text="??").upper(),
        "nome_regiao": fake.random_element(
            elements=("Norte", "Nordeste", "Centro-Oeste", "Sudeste", "Sul")
        ),
    }


def create_uf_db(session, data=None) -> UFModel:
    """Create test UF record"""
    data = data or make_uf_data()
    uf = UFModel(**data)
    session.add(uf)
    session.commit()
    return uf


class TestUFCollection:
    def test_get_empty(self, client):
        """Test Retrieve all entries when database is empty is successful."""
        response = client.get(url)
        assert response.status_code == 200
        assert response.json == []

    def test_list_with_data(self, client, session):
        """Test Retrieve all entries when database has data is successful."""
        created_uf = create_uf_db(session)

        response = client.get(url)
        assert response.status_code == 200
        assert isinstance(response.json, list)
        assert len(response.json) > 0

        listed_uf = response.json[0]["data"]
        assert listed_uf["id"] == created_uf.id
        assert listed_uf["nome"] == created_uf.nome

    def test_create_valid(self, client, session):
        """Test creating a valid UF"""
        uf_data = make_uf_data()
        response = client.post(url, json=uf_data)

        assert response.status_code == 201
        assert response.json["data"]["nome"] == uf_data["nome"]
        assert response.json["data"]["codigo"] == uf_data["codigo"]
        assert response.json["data"]["sigla"] == uf_data["sigla"]
        assert response.json["data"]["nome_regiao"] == uf_data["nome_regiao"]
        assert isinstance(response.json["data"]["id"], int)

        # Verify database
        db_uf = session.query(UFModel).filter_by(id=response.json["data"]["id"]).first()
        assert db_uf is not None
        assert db_uf.codigo == uf_data["codigo"]

    def test_create_duplicate(self, client, session):
        """Test Create an entry with an existing codigo fails."""
        uf_data = make_uf_data()
        create_uf_db(session, uf_data)
        response = client.post(url, json=uf_data)

        assert response.status_code == 422
        assert "Já existe uma UF com esse código" in response.json["message"]

    @pytest.mark.parametrize(
        "payload, missing_field",
        [
            ({"codigo": "1234"}, "nome"),
            ({"nome": "UF Test"}, "codigo"),
            ({"sigla": "UF Test"}, "nome"),
            ({"nome_regiao": "UF Test"}, "nome"),
            ({}, "nome"),
        ],
    )
    def test_create_missing_fields(self, client, payload, missing_field, session):
        """Test validation for missing required fields"""
        response = client.post(url, json=payload)

        assert response.status_code == 400
        assert "message" in response.json
        assert missing_field in response.json["message"]


class TestUFResource:
    """Tests for single UF resource endpoints (/api/ufs/<id>)"""

    @pytest.fixture
    def existing_uf(self, session) -> UFModel:
        """Fixture providing an existing UF."""
        return create_uf_db(session)

    def test_get_existing(self, client, existing_uf):
        """Test getting an existing UF."""
        response = client.get(f"{url}{existing_uf.id}")

        assert response.status_code == 200
        assert response.json["data"]["id"] == existing_uf.id
        assert response.json["data"]["nome"] == existing_uf.nome
        assert response.json["data"]["codigo"] == existing_uf.codigo
        assert response.json["data"]["sigla"] == existing_uf.sigla
        assert response.json["data"]["nome_regiao"] == existing_uf.nome_regiao

    def test_get_nonexistent(self, client):
        """Test getting non-existent UF."""
        response = client.get(f"{url}9999")
        assert response.status_code == 404
        assert "Nenhum registro encontrado" in response.json["message"]

    def test_update_same_codigo(self, client, existing_uf, session):
        """Test Update an existing entry with a different codigo is successful."""
        update_data = {
            "nome": "Updated UF",
            "codigo": existing_uf.codigo,
            "sigla": "UU",
            "nome_regiao": "NEW-REG",
        }
        response = client.put(f"{url}{existing_uf.id}", json=update_data)
        assert response.status_code == 204

        # Verify update
        session.refresh(existing_uf)
        assert existing_uf.nome == update_data["nome"]
        assert existing_uf.codigo == update_data["codigo"]
        assert existing_uf.sigla == update_data["sigla"]
        assert existing_uf.nome_regiao == update_data["nome_regiao"]

    def test_update_different_codigo(self, client, existing_uf, session):
        """Test Update an existing entry with a different codigo is successful."""
        update_data = {
            "nome": "Updated UF",
            "codigo": "5678",
            "sigla": "UU",
            "nome_regiao": "NEW-REG",
        }
        response = client.put(f"{url}{existing_uf.id}", json=update_data)
        assert response.status_code == 204

        # Verify update
        session.refresh(existing_uf)
        assert existing_uf.nome == update_data["nome"]
        assert existing_uf.codigo == update_data["codigo"]
        assert existing_uf.sigla == update_data["sigla"]
        assert existing_uf.nome_regiao == update_data["nome_regiao"]

    def test_update_nonexistent(self, client):
        """Test updating non-existent UF"""
        response = client.put(f"{url}9999", json=make_uf_data())
        assert response.status_code == 404
        assert "Nenhum registro encontrado" in response.json["message"]

    def test_update_existent_codigo(self, client, existing_uf, session):
        """Test updating with an existent codigo fails."""
        data = {
            "nome": "UF Test 2",
            "codigo": "4321",
            "sigla": "U2",
            "nome_regiao": "REG2",
        }
        uf2 = create_uf_db(session, data)

        data["codigo"] = existing_uf.codigo
        response = client.put(f"{url}{uf2.id}", json=data)

        assert response.status_code == 422
        assert "Já existe uma UF com esse código" in response.json["message"]

    def test_delete_existing(self, client, existing_uf, session):
        """Test deleting existing UF"""
        response = client.delete(f"{url}{existing_uf.id}")

        assert response.status_code == 204

        # Verify deletion
        assert session.get(UFModel, existing_uf.id) is None

    def test_delete_nonexistent(self, client):
        """Test deleting non-existent UF"""
        response = client.delete(f"{url}9999")

        assert response.status_code == 404
        assert "Nenhum registro encontrado" in response.json["message"]
