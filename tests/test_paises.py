## Tests for Pais Collection

import pytest


url = "/api/paises/"


def test_get_paises_empty(client):
    """Test Retrieve all entries when database is empty is successful."""
    response = client.get(url)
    assert response.status_code == 200
    assert response.json == []


@pytest.mark.dependency(name="create_pais")
def test_create_pais(client) -> int:
    """Test Create a new valid entry is successful."""
    response = create_pais(client)

    assert response.status_code == 201
    assert "id" in response.json["data"]
    assert response.json["data"]["nome"] == "Pais Test"
    assert response.json["data"]["codigo"] == "1234"


@pytest.mark.dependency(depends=["create_pais"])
def test_get_paises_with_data(client):
    """Test Retrieve all entries when database has data is successful."""
    # Create a Pais entry
    create_pais(client)

    # Retrieve all Paises
    response = client.get(url)

    assert response.status_code == 200
    assert isinstance(response.json, list)
    assert len(response.json) > 0
    assert any(
        pais["data"]["nome"] == "Pais Test" and pais["data"]["codigo"] == "1234"
        for pais in response.json
    )


def test_create_duplicate_pais(client):
    """Test Create an entry with an existing codigo fails."""
    create_pais(client)
    response = create_pais(client)

    assert response.status_code == 422
    assert response.json["message"] == "Já existe uma Pais com esse código."


@pytest.mark.parametrize(
    "payload, missing_field",
    [
        ({"codigo": "1234"}, "nome"),
        ({"nome": "Pais Test"}, "codigo"),
        ({}, "nome"),
    ],
)
def test_create_pais_missing_fields(client, payload, missing_field):
    """Test Create an entry with missing nome or codigo fails."""
    response = create_pais(client, data=payload)

    assert response.status_code == 400
    assert "message" in response.json
    assert missing_field in response.json["message"]


## Tests for Pais
@pytest.mark.dependency(name="get_pais", depends=["create_pais"])
def test_get_existing_pais(client):
    """
    Test Retrieve a valid entry by ID is successful.
    Depends on test_create_pais.
    """
    pais = create_pais(client).json["data"]

    response = client.get(f"{url}{pais["id"]}")

    assert response.status_code == 200
    assert response.json["data"]["id"] == pais["id"]
    assert response.json["data"]["nome"] == "Pais Test"
    assert response.json["data"]["codigo"] == "1234"


def test_get_nonexistent_pais(client):
    """Test Retrieve a non-existent entry is successful."""
    response = client.get(f"{url}999")

    assert response.status_code == 404
    assert response.json["message"] == "Nenhum registro encontrado."


@pytest.mark.dependency(depends=["create_pais", "get_pais"])
def test_update_pais_with_different_codigo(client):
    """
    Test Update an existing entry with a different codigo is successful.
    Depends on test_create_pais and test_get_existing_pais.
    """
    pais = create_pais(client).json["data"]

    response = client.put(
        f"{url}{pais['id']}", json={"nome": "Updated", "codigo": "5678"}
    )

    updated_pais = client.get(f"{url}{pais["id"]}").json["data"]
    assert response.status_code == 204
    assert response.data == b""
    assert updated_pais["id"] == pais["id"]
    assert updated_pais["nome"] == "Updated"
    assert updated_pais["codigo"] == "5678"


@pytest.mark.dependency(depends=["create_pais", "get_pais"])
def test_update_pais_with_same_codigo(client):
    """
    Test Update an existing entry with the original codigo is successful.
    Depends on test_create_pais and test_get_existing_pais.
    """
    pais = create_pais(client).json["data"]

    response = client.put(
        f"{url}{pais['id']}", json={"nome": "Updated", "codigo": "1234"}
    )

    updated_pais = client.get(f"{url}{pais["id"]}").json["data"]
    assert response.status_code == 204
    assert response.data == b""
    assert updated_pais["id"] == pais["id"]
    assert updated_pais["nome"] == "Updated"
    assert updated_pais["codigo"] == "1234"


def test_update_nonexistent_pais(client):
    """Test updating a non-existent Pais fails."""
    non_existent_id = 9999
    data = make_pais_data()

    response = client.put(f"{url}{non_existent_id}", json=data)

    assert response.status_code == 404
    assert response.json["message"] == "Nenhum registro encontrado."


@pytest.mark.dependency(depends=["create_pais"])
def test_update_pais_with_existing_codigo(client):
    """Test updating a Pais with a codigo fails."""

    # Create two Paises
    data1 = {"nome": "Pais One", "codigo": "1111"}
    data2 = {"nome": "Pais Two", "codigo": "2222"}

    pais1 = create_pais(client, data=data1).json["data"]
    pais2 = create_pais(client, data=data2).json["data"]

    # Attempt to update Pais2 with Pais1's codigo
    response = client.put(
        f"{url}{pais2["id"]}", json={"nome": "Updated Pais", "codigo": pais1["codigo"]}
    )

    assert response.status_code == 422
    assert response.json["message"] == "Já existe uma Pais com esse código."


@pytest.mark.dependency(depends=["create_pais"])
def test_delete_existing_pais(client):
    """Test deleting an existing Pais is successful."""

    # Create a Pais
    pais = create_pais(client).json["data"]

    # Delete the created Pais
    response = client.delete(f"{url}{pais["id"]}")

    assert response.status_code == 204
    assert response.data == b""

    # Try retrieving it to confirm deletion
    get_response = client.get(f"{url}{pais["id"]}")
    assert get_response.status_code == 404


def test_delete_nonexistent_pais(client):
    """Test deleting a non-existent Pais fails."""

    non_existent_id = 9999
    response = client.delete(f"{url}{non_existent_id}")

    assert response.status_code == 404
    assert response.json["message"] == "Nenhum registro encontrado."


#


def make_pais_data() -> dict:
    """Make an object of data for body requests."""
    return {"nome": "Pais Test", "codigo": "1234"}


def create_pais(client, data=make_pais_data()) -> dict:
    """Create an entry in the database."""
    return client.post(url, json=data)
