## Tests for SH4 Collection

import pytest

from src.sh4s.model import SH4Model


url = "/api/sh4s/"


def test_get_sh4s_empty(client):
    """Test Retrieve all entries when database is empty is successful."""
    response = client.get(url)
    assert response.status_code == 200
    assert response.json == []


@pytest.mark.dependency(name="create_sh4")
def test_create_sh4(client) -> int:
    """Test Create a new valid entry is successful."""
    data = {"nome": "SH4 Test", "codigo": "1234"}
    response = client.post(url, json=data)

    assert response.status_code == 201
    assert "id" in response.json["data"]
    assert response.json["data"]["nome"] == "SH4 Test"
    assert response.json["data"]["codigo"] == "1234"


@pytest.mark.dependency(depends=["create_sh4"])
def test_get_sh4s_with_data(client):
    """Test Retrieve all entries when database has data is successful."""
    # Create a SH4 entry
    data = {"nome": "SH4 Test", "codigo": "1234"}
    client.post(url, json=data)  # Creating the entry

    # Retrieve all SH4s
    response = client.get(url)

    assert response.status_code == 200
    assert isinstance(response.json, list)
    assert len(response.json) > 0
    assert any(
        sh4["data"]["nome"] == "SH4 Test" and sh4["data"]["codigo"] == "1234"
        for sh4 in response.json
    )


def test_create_duplicate_sh4(client):
    """Test Create an entry with an existing codigo fails."""
    data = {"nome": "SH4 Test", "codigo": "1234"}
    client.post(url, json=data)
    response = client.post(url, json=data)

    assert response.status_code == 422
    assert response.json["message"] == "Já existe uma SH4 com esse código."


@pytest.mark.parametrize(
    "payload, missing_field",
    [
        ({"codigo": "1234"}, "nome"),
        ({"nome": "SH4 Test"}, "codigo"),
        ({}, "nome"),
    ],
)
def test_create_sh4_missing_fields(client, payload, missing_field):
    """Test Create an entry with missing nome or codigo fails."""
    response = client.post(url, json=payload)

    assert response.status_code == 400
    assert "message" in response.json
    assert missing_field in response.json["message"]


## Tests for SH4
@pytest.mark.dependency(name="get_sh4", depends=["create_sh4"])
def test_get_existing_sh4(client):
    """
    Test Retrieve a valid entry by ID is successful.
    Depends on test_create_sh4.
    """
    data = {"nome": "SH4 Test", "codigo": "1234"}
    sh4 = client.post(url, json=data).json["data"]

    response = client.get(f"{url}{sh4["id"]}")

    assert response.status_code == 200
    assert response.json["data"]["id"] == sh4["id"]
    assert response.json["data"]["nome"] == "SH4 Test"
    assert response.json["data"]["codigo"] == "1234"


def test_get_nonexistent_sh4(client):
    """Test Retrieve a non-existent entry is successful."""
    response = client.get(f"{url}999")

    assert response.status_code == 404
    assert response.json["message"] == "Nenhum registro encontrado."


@pytest.mark.dependency(depends=["create_sh4", "get_sh4"])
def test_update_sh4_with_different_codigo(client):
    """
    Test Update an existing entry with a different codigo is successful.
    Depends on test_create_sh4 and test_get_existing_sh4.
    """
    data = {"nome": "SH4 Test", "codigo": "1234"}
    sh4 = client.post(url, json=data).json["data"]

    response = client.put(
        f"{url}{sh4['id']}", json={"nome": "Updated", "codigo": "5678"}
    )

    updated_sh4 = client.get(f"{url}{sh4["id"]}").json["data"]
    assert response.status_code == 204
    assert response.data == b""
    assert updated_sh4["id"] == sh4["id"]
    assert updated_sh4["nome"] == "Updated"
    assert updated_sh4["codigo"] == "5678"


@pytest.mark.dependency(depends=["create_sh4", "get_sh4"])
def test_update_sh4_with_same_codigo(client):
    """
    Test Update an existing entry with the original codigo is successful.
    Depends on test_create_sh4 and test_get_existing_sh4.
    """
    data = {"nome": "SH4 Test", "codigo": "1234"}
    sh4 = client.post(url, json=data).json["data"]

    response = client.put(
        f"{url}{sh4['id']}", json={"nome": "Updated", "codigo": "1234"}
    )

    updated_sh4 = client.get(f"{url}{sh4["id"]}").json["data"]
    assert response.status_code == 204
    assert response.data == b""
    assert updated_sh4["id"] == sh4["id"]
    assert updated_sh4["nome"] == "Updated"
    assert updated_sh4["codigo"] == "1234"


def test_update_nonexistent_sh4(client):
    """Test updating a non-existent SH4 fails."""
    non_existent_id = 9999
    data = {"nome": "SH4 Test", "codigo": "1234"}

    response = client.put(f"{url}{non_existent_id}", json=data)

    assert response.status_code == 404
    assert response.json["message"] == "Nenhum registro encontrado."


@pytest.mark.dependency(depends=["create_sh4"])
def test_update_sh4_with_existing_codigo(client):
    """Test updating a SH4 with a codigo fails."""

    # Create two SH4s
    data1 = {"nome": "SH4 One", "codigo": "1111"}
    data2 = {"nome": "SH4 Two", "codigo": "2222"}

    sh41 = client.post(url, json=data1).json["data"]
    sh42 = client.post(url, json=data2).json["data"]

    # Attempt to update SH42 with SH41's codigo
    response = client.put(
        f"{url}{sh42["id"]}", json={"nome": "Updated SH4", "codigo": "1111"}
    )

    assert response.status_code == 422
    assert response.json["message"] == "Já existe uma SH4 com esse código."


@pytest.mark.dependency(depends=["create_sh4"])
def test_delete_existing_sh4(client):
    """Test deleting an existing SH4 is successful."""

    # Create a SH4
    data = {"nome": "SH4 Test", "codigo": "1234"}
    sh4 = client.post(url, json=data).json["data"]

    # Delete the created SH4
    response = client.delete(f"{url}{sh4["id"]}")

    assert response.status_code == 204
    assert response.data == b""

    # Try retrieving it to confirm deletion
    get_response = client.get(f"{url}{sh4["id"]}")
    assert get_response.status_code == 404


def test_delete_nonexistent_sh4(client):
    """Test deleting a non-existent SH4 fails."""

    non_existent_id = 9999
    response = client.delete(f"{url}{non_existent_id}")

    assert response.status_code == 404
    assert response.json["message"] == "Nenhum registro encontrado."
