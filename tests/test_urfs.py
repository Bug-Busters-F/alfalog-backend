## Tests for URF Collection

import pytest

from src.urfs.model import URFModel


url = "/api/urfs/"


def test_get_urfs_empty(client):
    """Test Retrieve all entries when database is empty is successful."""
    response = client.get(url)
    assert response.status_code == 200
    assert response.json == []


@pytest.mark.dependency(depends=["create_urf"])
def test_get_urfs_with_data(client):
    """Test Retrieve all entries when database has data is successful."""
    # Create a URF entry
    data = {"nome": "URF Test", "codigo": "1234"}
    client.post(url, json=data)  # Creating the entry

    # Retrieve all URFs
    response = client.get(url)

    assert response.status_code == 200
    assert isinstance(response.json, list)
    assert len(response.json) > 0
    assert any(
        urf["data"]["nome"] == "URF Test" and urf["data"]["codigo"] == "1234"
        for urf in response.json
    )


@pytest.mark.dependency(name="create_urf")
def test_create_urf(client) -> int:
    """Test Create a new valid entry is successful."""
    data = {"nome": "URF Test", "codigo": "1234"}
    response = client.post(url, json=data)

    assert response.status_code == 201
    assert "id" in response.json["data"]
    assert response.json["data"]["nome"] == "URF Test"
    assert response.json["data"]["codigo"] == "1234"


def test_create_duplicate_urf(client):
    """Test Create an entry with an existing codigo fails."""
    data = {"nome": "URF Test", "codigo": "1234"}
    client.post(url, json=data)
    response = client.post(url, json=data)

    assert response.status_code == 422
    assert response.json["message"] == "Já existe uma URF com esse código."


@pytest.mark.parametrize(
    "payload, missing_field",
    [
        ({"codigo": "1234"}, "nome"),
        ({"nome": "URF Test"}, "codigo"),
        ({}, "nome"),
    ],
)
def test_create_urf_missing_fields(client, payload, missing_field):
    """Test Create an entry with missing nome or codigo fails."""
    response = client.post(url, json=payload)

    assert response.status_code == 400
    assert "message" in response.json
    assert missing_field in response.json["message"]


## Tests for URF
@pytest.mark.dependency(name="get_urf", depends=["create_urf"])
def test_get_existing_urf(client):
    """
    Test Retrieve a valid entry by ID is successful.
    Depends on test_create_urf.
    """
    data = {"nome": "URF Test", "codigo": "1234"}
    urf = client.post(url, json=data).json["data"]

    response = client.get(f"{url}{urf["id"]}")

    assert response.status_code == 200
    assert response.json["data"]["id"] == urf["id"]
    assert response.json["data"]["nome"] == "URF Test"
    assert response.json["data"]["codigo"] == "1234"


def test_get_nonexistent_urf(client):
    """Test Retrieve a non-existent entry is successful."""
    response = client.get(f"{url}999")

    assert response.status_code == 404
    assert response.json["message"] == "Nenhum registro encontrado."


@pytest.mark.dependency(depends=["create_urf", "get_urf"])
def test_update_urf_with_different_codigo(client):
    """
    Test Update an existing entry with a different codigo is successful.
    Depends on test_create_urf and test_get_existing_urf.
    """
    data = {"nome": "URF Test", "codigo": "1234"}
    urf = client.post(url, json=data).json["data"]

    response = client.put(
        f"{url}{urf['id']}", json={"nome": "Updated", "codigo": "5678"}
    )

    updated_urf = client.get(f"{url}{urf["id"]}").json["data"]
    assert response.status_code == 204
    assert response.data == b""
    assert updated_urf["id"] == urf["id"]
    assert updated_urf["nome"] == "Updated"
    assert updated_urf["codigo"] == "5678"


@pytest.mark.dependency(depends=["create_urf", "get_urf"])
def test_update_urf_with_same_codigo(client):
    """
    Test Update an existing entry with the original codigo is successful.
    Depends on test_create_urf and test_get_existing_urf.
    """
    data = {"nome": "URF Test", "codigo": "1234"}
    urf = client.post(url, json=data).json["data"]

    response = client.put(
        f"{url}{urf['id']}", json={"nome": "Updated", "codigo": "1234"}
    )

    updated_urf = client.get(f"{url}{urf["id"]}").json["data"]
    assert response.status_code == 204
    assert response.data == b""
    assert updated_urf["id"] == urf["id"]
    assert updated_urf["nome"] == "Updated"
    assert updated_urf["codigo"] == "1234"


def test_update_nonexistent_urf(client):
    """Test updating a non-existent URF fails."""
    non_existent_id = 9999
    data = {"nome": "Updated Name", "codigo": "5678"}

    response = client.put(f"{url}{non_existent_id}", json=data)

    assert response.status_code == 404
    assert response.json["message"] == "Nenhum registro encontrado."


@pytest.mark.dependency(depends=["create_urf"])
def test_update_urf_with_existing_codigo(client):
    """Test updating a URF with a codigo fails."""

    # Create two URFs
    data1 = {"nome": "URF One", "codigo": "1111"}
    data2 = {"nome": "URF Two", "codigo": "2222"}

    urf1 = client.post(url, json=data1).json["data"]
    urf2 = client.post(url, json=data2).json["data"]

    # Attempt to update URF2 with URF1's codigo
    response = client.put(
        f"{url}{urf2["id"]}", json={"nome": "Updated URF", "codigo": "1111"}
    )

    assert response.status_code == 422
    assert response.json["message"] == "Já existe uma URF com esse código."


@pytest.mark.dependency(depends=["create_urf"])
def test_delete_existing_urf(client):
    """Test deleting an existing URF is successful."""

    # Create a URF
    data = {"nome": "URF to Delete", "codigo": "9999"}
    urf = client.post(url, json=data).json["data"]

    # Delete the created URF
    response = client.delete(f"{url}{urf["id"]}")

    assert response.status_code == 204
    assert response.data == b""

    # Try retrieving it to confirm deletion
    get_response = client.get(f"{url}{urf["id"]}")
    assert get_response.status_code == 404


def test_delete_nonexistent_urf(client):
    """Test deleting a non-existent URF fails."""

    non_existent_id = 9999
    response = client.delete(f"{url}{non_existent_id}")

    assert response.status_code == 404
    assert response.json["message"] == "Nenhum registro encontrado."
