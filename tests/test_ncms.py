## Tests for NCM Collection

import pytest

from src.ncms.model import NCMModel


url = "/api/ncms/"


def test_get_ncms_empty(client):
    """Test Retrieve all entries when database is empty is successful."""
    response = client.get(url)
    assert response.status_code == 200
    assert response.json == []


@pytest.mark.dependency(name="create_ncm")
def test_create_ncm(client) -> int:
    """Test Create a new valid entry is successful."""
    data = {"codigo": "1234", "descricao": "NCM Test"}
    response = client.post(url, json=data)

    assert response.status_code == 201
    assert "id" in response.json["data"]
    assert response.json["data"]["codigo"] == "1234"
    assert response.json["data"]["descricao"] == "NCM Test"


@pytest.mark.dependency(depends=["create_ncm"])
def test_get_ncms_with_data(client):
    """Test Retrieve all entries when database has data is successful."""
    # Create a NCM entry
    data = {"codigo": "1234", "descricao": "NCM Test"}
    client.post(url, json=data)  # Creating the entry

    # Retrieve all NCMs
    response = client.get(url)

    assert response.status_code == 200
    assert isinstance(response.json, list)
    assert len(response.json) > 0
    assert any(
        ncm["data"]["codigo"] == "1234" and ncm["data"]["descricao"] == "NCM Test"
        for ncm in response.json
    )


def test_create_duplicate_ncm(client):
    """Test Create an entry with an existing codigo fails."""
    data = {"codigo": "1234", "descricao": "NCM Test"}
    client.post(url, json=data)
    response = client.post(url, json=data)

    assert response.status_code == 422
    assert response.json["message"] == "Já existe uma NCM com esse código."


@pytest.mark.parametrize(
    "payload, missing_field",
    [
        ({"descricao": "NCM Test"}, "codigo"),
        ({"codigo": "1234"}, "descricao"),
        ({}, "codigo"),
    ],
)
def test_create_ncm_missing_fields(client, payload, missing_field):
    """Test Create an entry with missing nome or codigo fails."""
    response = client.post(url, json=payload)

    assert response.status_code == 400
    assert "message" in response.json
    assert missing_field in response.json["message"]


## Tests for NCM
@pytest.mark.dependency(name="get_ncm", depends=["create_ncm"])
def test_get_existing_ncm(client):
    """
    Test Retrieve a valid entry by ID is successful.
    Depends on test_create_ncm.
    """
    data = {"codigo": "1234", "descricao": "NCM Test"}
    ncm = client.post(url, json=data).json["data"]

    response = client.get(f"{url}{ncm["id"]}")

    assert response.status_code == 200
    assert response.json["data"]["id"] == ncm["id"]
    assert response.json["data"]["codigo"] == "1234"
    assert response.json["data"]["descricao"] == "NCM Test"


def test_get_nonexistent_ncm(client):
    """Test Retrieve a non-existent entry is successful."""
    response = client.get(f"{url}999")

    assert response.status_code == 404
    assert response.json["message"] == "Nenhum registro encontrado."


@pytest.mark.dependency(depends=["create_ncm", "get_ncm"])
def test_update_ncm_with_different_codigo(client):
    """
    Test Update an existing entry with a different codigo is successful.
    Depends on test_create_ncm and test_get_existing_ncm.
    """
    data = {"codigo": "1234", "descricao": "NCM Test"}
    ncm = client.post(url, json=data).json["data"]

    response = client.put(
        f"{url}{ncm['id']}", json={"codigo": "5678", "descricao": "Updated"}
    )

    updated_ncm = client.get(f"{url}{ncm["id"]}").json["data"]
    assert response.status_code == 204
    assert response.data == b""
    assert updated_ncm["id"] == ncm["id"]
    assert updated_ncm["codigo"] == "5678"
    assert updated_ncm["descricao"] == "Updated"


@pytest.mark.dependency(depends=["create_ncm", "get_ncm"])
def test_update_ncm_with_same_codigo(client):
    """
    Test Update an existing entry with the original codigo is successful.
    Depends on test_create_ncm and test_get_existing_ncm.
    """
    data = {"codigo": "1234", "descricao": "NCM Test"}
    ncm = client.post(url, json=data).json["data"]

    response = client.put(
        f"{url}{ncm['id']}", json={"codigo": "1234", "descricao": "Updated"}
    )

    updated_ncm = client.get(f"{url}{ncm["id"]}").json["data"]
    assert response.status_code == 204
    assert response.data == b""
    assert updated_ncm["id"] == ncm["id"]
    assert updated_ncm["codigo"] == "1234"
    assert updated_ncm["descricao"] == "Updated"


def test_update_nonexistent_ncm(client):
    """Test updating a non-existent NCM fails."""
    non_existent_id = 9999
    data = {"codigo": "1234", "descricao": "NCM Test"}

    response = client.put(f"{url}{non_existent_id}", json=data)

    assert response.status_code == 404
    assert response.json["message"] == "Nenhum registro encontrado."


@pytest.mark.dependency(depends=["create_ncm"])
def test_update_ncm_with_existing_codigo(client):
    """Test updating a NCM with a codigo fails."""

    # Create two NCMs
    data1 = {"codigo": "1111", "descricao": "NCM One"}
    data2 = {"codigo": "2222", "descricao": "NCM Two"}

    ncm1 = client.post(url, json=data1).json["data"]
    ncm2 = client.post(url, json=data2).json["data"]

    # Attempt to update NCM2 with NCM1's codigo
    response = client.put(
        f"{url}{ncm2["id"]}", json={"codigo": "1111", "descricao": "Updated NCM"}
    )

    assert response.status_code == 422
    assert response.json["message"] == "Já existe uma NCM com esse código."


@pytest.mark.dependency(depends=["create_ncm"])
def test_delete_existing_ncm(client):
    """Test deleting an existing NCM is successful."""

    # Create a NCM
    data = {"codigo": "1234", "descricao": "NCM Test"}
    ncm = client.post(url, json=data).json["data"]

    # Delete the created NCM
    response = client.delete(f"{url}{ncm["id"]}")

    assert response.status_code == 204
    assert response.data == b""

    # Try retrieving it to confirm deletion
    get_response = client.get(f"{url}{ncm["id"]}")
    assert get_response.status_code == 404


def test_delete_nonexistent_ncm(client):
    """Test deleting a non-existent NCM fails."""

    non_existent_id = 9999
    response = client.delete(f"{url}{non_existent_id}")

    assert response.status_code == 404
    assert response.json["message"] == "Nenhum registro encontrado."
