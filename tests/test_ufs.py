## Tests for UF Collection

import pytest


url = "/api/ufs/"


def test_get_ufs_empty(client):
    """Test Retrieve all entries when database is empty is successful."""
    response = client.get(url)
    assert response.status_code == 200
    assert response.json == []


@pytest.mark.dependency(name="create_uf")
def test_create_uf(client) -> int:
    """Test Create a new valid entry is successful."""
    response = create_uf(client)

    assert response.status_code == 201
    assert "id" in response.json["data"]
    assert response.json["data"]["nome"] == "UF Test"
    assert response.json["data"]["codigo"] == "1234"
    assert response.json["data"]["sigla"] == "UF"
    assert response.json["data"]["nome_regiao"] == "REG"


@pytest.mark.dependency(depends=["create_uf"])
def test_get_ufs_with_data(client):
    """Test Retrieve all entries when database has data is successful."""
    create_uf(client)

    # Retrieve all UFs
    response = client.get(url)

    assert response.status_code == 200
    assert isinstance(response.json, list)
    assert len(response.json) > 0
    assert any(
        uf["data"]["nome"] == "UF Test" and uf["data"]["codigo"] == "1234"
        for uf in response.json
    )


def test_create_duplicate_uf(client):
    """Test Create an entry with an existing codigo fails."""
    create_uf(client)
    response = create_uf(client)

    assert response.status_code == 422
    assert response.json["message"] == "Já existe uma UF com esse código."


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
def test_create_uf_missing_fields(client, payload, missing_field):
    """Test Create an entry with missing nome or codigo fails."""
    response = create_uf(client, data=payload)

    assert response.status_code == 400
    assert "message" in response.json
    assert missing_field in response.json["message"]


## Tests for UF
@pytest.mark.dependency(name="get_uf", depends=["create_uf"])
def test_get_existing_uf(client):
    """
    Test Retrieve a valid entry by ID is successful.
    Depends on test_create_uf.
    """
    uf = create_uf(client).json["data"]

    response = client.get(f"{url}{uf["id"]}")

    assert response.status_code == 200
    assert response.json["data"]["id"] == uf["id"]
    assert response.json["data"]["nome"] == "UF Test"
    assert response.json["data"]["codigo"] == "1234"
    assert response.json["data"]["sigla"] == "UF"
    assert response.json["data"]["nome_regiao"] == "REG"


def test_get_nonexistent_uf(client):
    """Test Retrieve a non-existent entry is successful."""
    response = client.get(f"{url}999")

    assert response.status_code == 404
    assert response.json["message"] == "Nenhum registro encontrado."


@pytest.mark.dependency(depends=["create_uf", "get_uf"])
def test_update_uf_with_different_codigo(client):
    """
    Test Update an existing entry with a different codigo is successful.
    Depends on test_create_uf and test_get_existing_uf.
    """
    uf = create_uf(client).json["data"]

    response = client.put(
        f"{url}{uf['id']}",
        json={
            "nome": "Updated",
            "codigo": "5678",
            "sigla": "UF",
            "nome_regiao": "REG",
        },
    )

    updated_uf = client.get(f"{url}{uf["id"]}").json["data"]
    assert response.status_code == 204
    assert response.data == b""
    assert updated_uf["id"] == uf["id"]
    assert updated_uf["nome"] == "Updated"
    assert updated_uf["codigo"] == "5678"
    assert updated_uf["sigla"] == "UF"
    assert updated_uf["nome_regiao"] == "REG"


@pytest.mark.dependency(depends=["create_uf", "get_uf"])
def test_update_uf_with_same_codigo(client):
    """
    Test Update an existing entry with the original codigo is successful.
    Depends on test_create_uf and test_get_existing_uf.
    """
    uf = create_uf(client).json["data"]

    response = client.put(
        f"{url}{uf['id']}",
        json={
            "nome": "Updated",
            "codigo": uf["codigo"],
            "sigla": "UF",
            "nome_regiao": "REG",
        },
    )

    updated_uf = client.get(f"{url}{uf["id"]}").json["data"]
    assert response.status_code == 204
    assert response.data == b""
    assert updated_uf["id"] == uf["id"]
    assert updated_uf["nome"] == "Updated"
    assert updated_uf["codigo"] == "1234"
    assert updated_uf["sigla"] == "UF"
    assert updated_uf["nome_regiao"] == "REG"


def test_update_nonexistent_uf(client):
    """Test updating a non-existent UF fails."""
    non_existent_id = 9999

    data = make_uf_data()

    response = client.put(f"{url}{non_existent_id}", json=data)

    assert response.status_code == 404
    assert response.json["message"] == "Nenhum registro encontrado."


@pytest.mark.dependency(depends=["create_uf"])
def test_update_uf_with_existing_codigo(client):
    """Test updating a UF with a codigo fails."""

    # Create two UFs
    data1 = {
        "nome": "UF One",
        "codigo": "1111",
        "sigla": "UF1",
        "nome_regiao": "REG A",
    }
    data2 = {
        "nome": "UF Two",
        "codigo": "2222",
        "sigla": "UF2",
        "nome_regiao": "REG B",
    }

    uf1 = create_uf(client, data=data1).json["data"]
    uf2 = create_uf(client, data=data2).json["data"]

    # Attempt to update UF2 with UF1's codigo
    uf2["codigo"] = uf1["codigo"]
    response = client.put(
        f"{url}{uf2["id"]}",
        json={
            "nome": "Updated UF",
            "codigo": uf1["codigo"],
            "sigla": uf2["sigla"],
            "nome_regiao": uf2["nome_regiao"],
        },
    )

    assert response.status_code == 422
    assert response.json["message"] == "Já existe uma UF com esse código."


@pytest.mark.dependency(depends=["create_uf"])
def test_delete_existing_uf(client):
    """Test deleting an existing UF is successful."""

    uf = create_uf(client).json["data"]

    # Delete the created UF
    response = client.delete(f"{url}{uf["id"]}")

    assert response.status_code == 204
    assert response.data == b""

    # Try retrieving it to confirm deletion
    get_response = client.get(f"{url}{uf["id"]}")
    assert get_response.status_code == 404


def test_delete_nonexistent_uf(client):
    """Test deleting a non-existent UF fails."""

    non_existent_id = 9999
    response = client.delete(f"{url}{non_existent_id}")

    assert response.status_code == 404
    assert response.json["message"] == "Nenhum registro encontrado."


def make_uf_data() -> dict:
    """Make an object of data for body requests."""
    return {
        "nome": "UF Test",
        "codigo": "1234",
        "sigla": "UF",
        "nome_regiao": "REG",
    }


def create_uf(client, data=make_uf_data()) -> dict:
    """Create an entry in the database."""
    return client.post(url, json=data)
