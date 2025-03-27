## Tests for Via Collection

import pytest


url = "/api/vias/"


def test_get_vias_empty(client):
    """Test Retrieve all entries when database is empty is successful."""
    response = client.get(url)
    assert response.status_code == 200
    assert response.json == []


@pytest.mark.dependency(name="create_via")
def test_create_via(client) -> int:
    """Test Create a new valid entry is successful."""
    response = create_via(client)

    assert response.status_code == 201
    assert "id" in response.json["data"]
    assert response.json["data"]["nome"] == "Via Test"
    assert response.json["data"]["codigo"] == "1234"


@pytest.mark.dependency(depends=["create_via"])
def test_get_vias_with_data(client):
    """Test Retrieve all entries when database has data is successful."""
    create_via(client)

    # Retrieve all Vias
    response = client.get(url)

    assert response.status_code == 200
    assert isinstance(response.json, list)
    assert len(response.json) > 0
    assert any(
        via["data"]["nome"] == "Via Test" and via["data"]["codigo"] == "1234"
        for via in response.json
    )


def test_create_duplicate_via(client):
    """Test Create an entry with an existing codigo fails."""
    create_via(client)
    response = create_via(client)

    assert response.status_code == 422
    assert response.json["message"] == "Já existe uma Via com esse código."


@pytest.mark.parametrize(
    "payload, missing_field",
    [
        ({"codigo": "1234"}, "nome"),
        ({"nome": "Via Test"}, "codigo"),
        ({}, "nome"),
    ],
)
def test_create_via_missing_fields(client, payload, missing_field):
    """Test Create an entry with missing nome or codigo fails."""
    response = create_via(client, data=payload)

    assert response.status_code == 400
    assert "message" in response.json
    assert missing_field in response.json["message"]


## Tests for Via
@pytest.mark.dependency(name="get_via", depends=["create_via"])
def test_get_existing_via(client):
    """
    Test Retrieve a valid entry by ID is successful.
    Depends on test_create_via.
    """
    via = create_via(client).json["data"]

    response = client.get(f"{url}{via["id"]}")

    assert response.status_code == 200
    assert response.json["data"]["id"] == via["id"]
    assert response.json["data"]["nome"] == "Via Test"
    assert response.json["data"]["codigo"] == "1234"


def test_get_nonexistent_via(client):
    """Test Retrieve a non-existent entry is successful."""
    response = client.get(f"{url}999")

    assert response.status_code == 404
    assert response.json["message"] == "Nenhum registro encontrado."


@pytest.mark.dependency(depends=["create_via", "get_via"])
def test_update_via_with_different_codigo(client):
    """
    Test Update an existing entry with a different codigo is successful.
    Depends on test_create_via and test_get_existing_via.
    """
    via = create_via(client).json["data"]

    response = client.put(
        f"{url}{via['id']}", json={"nome": "Updated", "codigo": "5678"}
    )

    updated_via = client.get(f"{url}{via["id"]}").json["data"]
    assert response.status_code == 204
    assert response.data == b""
    assert updated_via["id"] == via["id"]
    assert updated_via["nome"] == "Updated"
    assert updated_via["codigo"] == "5678"


@pytest.mark.dependency(depends=["create_via", "get_via"])
def test_update_via_with_same_codigo(client):
    """
    Test Update an existing entry with the original codigo is successful.
    Depends on test_create_via and test_get_existing_via.
    """
    via = create_via(client).json["data"]

    response = client.put(
        f"{url}{via['id']}", json={"nome": "Updated", "codigo": "1234"}
    )

    updated_via = client.get(f"{url}{via["id"]}").json["data"]
    assert response.status_code == 204
    assert response.data == b""
    assert updated_via["id"] == via["id"]
    assert updated_via["nome"] == "Updated"
    assert updated_via["codigo"] == "1234"


def test_update_nonexistent_via(client):
    """Test updating a non-existent Via fails."""
    non_existent_id = 9999
    data = make_via_data()

    response = client.put(f"{url}{non_existent_id}", json=data)

    assert response.status_code == 404
    assert response.json["message"] == "Nenhum registro encontrado."


@pytest.mark.dependency(depends=["create_via"])
def test_update_via_with_existing_codigo(client):
    """Test updating a Via with a codigo fails."""

    # Create two Vias
    data1 = {"nome": "Via One", "codigo": "1111"}
    data2 = {"nome": "Via Two", "codigo": "2222"}

    via1 = create_via(client, data=data1).json["data"]
    via2 = create_via(client, data=data2).json["data"]

    # Attempt to update Via2 with Via1's codigo
    via2["codigo"] = via1["codigo"]
    response = client.put(f"{url}{via2["id"]}", json=via2)

    assert response.status_code == 422
    assert response.json["message"] == "Já existe uma Via com esse código."


@pytest.mark.dependency(depends=["create_via"])
def test_delete_existing_via(client):
    """Test deleting an existing Via is successful."""

    via = create_via(client).json["data"]

    # Delete the created Via
    response = client.delete(f"{url}{via["id"]}")

    assert response.status_code == 204
    assert response.data == b""

    # Try retrieving it to confirm deletion
    get_response = client.get(f"{url}{via["id"]}")
    assert get_response.status_code == 404


def test_delete_nonexistent_via(client):
    """Test deleting a non-existent Via fails."""

    non_existent_id = 9999
    response = client.delete(f"{url}{non_existent_id}")

    assert response.status_code == 404
    assert response.json["message"] == "Nenhum registro encontrado."


def make_via_data() -> dict:
    """Make an object of data for body requests."""
    return {"nome": "Via Test", "codigo": "1234"}


def create_via(client, data=make_via_data()) -> dict:
    """Create an entry in the database."""
    return client.post(url, json=data)
