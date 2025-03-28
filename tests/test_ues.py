## Tests for UE Collection

import pytest


url = "/api/ues/"


def test_get_ues_empty(client):
    """Test Retrieve all entries when database is empty is successful."""
    response = client.get(url)
    assert response.status_code == 200
    assert response.json == []


@pytest.mark.dependency(name="create_ue")
def test_create_ue(client) -> int:
    """Test Create a new valid entry is successful."""
    response = create_ue(client)

    assert response.status_code == 201
    assert "id" in response.json["data"]
    assert response.json["data"]["nome"] == "UE Test"
    assert response.json["data"]["codigo"] == "1234"
    assert response.json["data"]["abreviacao"] == "UT"


@pytest.mark.dependency(depends=["create_ue"])
def test_get_ues_with_data(client):
    """Test Retrieve all entries when database has data is successful."""
    create_ue(client)

    # Retrieve all UEs
    response = client.get(url)

    assert response.status_code == 200
    assert isinstance(response.json, list)
    assert len(response.json) > 0
    assert any(
        ue["data"]["nome"] == "UE Test"
        and ue["data"]["codigo"] == "1234"
        and ue["data"]["abreviacao"] == "UT"
        for ue in response.json
    )


def test_create_duplicate_ue(client):
    """Test Create an entry with an existing codigo fails."""
    create_ue(client)
    response = create_ue(client)

    assert response.status_code == 422
    assert response.json["message"] == "Já existe uma UE com esse código."


@pytest.mark.parametrize(
    "payload, missing_field",
    [
        ({"codigo": "1234"}, "nome"),
        ({"nome": "UE Test"}, "codigo"),
        ({"abreviacao": "UT"}, "nome"),
        ({}, "nome"),
    ],
)
def test_create_ue_missing_fields(client, payload, missing_field):
    """Test Create an entry with missing nome or codigo fails."""
    response = create_ue(client, data=payload)

    assert response.status_code == 400
    assert "message" in response.json
    assert missing_field in response.json["message"]


## Tests for UE
@pytest.mark.dependency(name="get_ue", depends=["create_ue"])
def test_get_existing_ue(client):
    """
    Test Retrieve a valid entry by ID is successful.
    Depends on test_create_ue.
    """
    ue = create_ue(client).json["data"]

    response = client.get(f"{url}{ue["id"]}")

    assert response.status_code == 200
    assert response.json["data"]["id"] == ue["id"]
    assert response.json["data"]["nome"] == "UE Test"
    assert response.json["data"]["codigo"] == "1234"
    assert response.json["data"]["abreviacao"] == "UT"


def test_get_nonexistent_ue(client):
    """Test Retrieve a non-existent entry is successful."""
    response = client.get(f"{url}999")

    assert response.status_code == 404
    assert response.json["message"] == "Nenhum registro encontrado."


@pytest.mark.dependency(depends=["create_ue", "get_ue"])
def test_update_ue_with_different_codigo(client):
    """
    Test Update an existing entry with a different codigo is successful.
    Depends on test_create_ue and test_get_existing_ue.
    """
    ue = create_ue(client).json["data"]

    response = client.put(
        f"{url}{ue['id']}",
        json={"nome": "Updated", "codigo": "5678", "abreviacao": "UT2"},
    )

    updated_ue = client.get(f"{url}{ue["id"]}").json["data"]
    assert response.status_code == 204
    assert response.data == b""
    assert updated_ue["id"] == ue["id"]
    assert updated_ue["nome"] == "Updated"
    assert updated_ue["codigo"] == "5678"
    assert updated_ue["abreviacao"] == "UT2"


@pytest.mark.dependency(depends=["create_ue", "get_ue"])
def test_update_ue_with_same_codigo(client):
    """
    Test Update an existing entry with the original codigo is successful.
    Depends on test_create_ue and test_get_existing_ue.
    """
    ue = create_ue(client).json["data"]

    response = client.put(
        f"{url}{ue['id']}",
        json={
            "nome": "Updated",
            "codigo": ue["codigo"],
            "abreviacao": ue["abreviacao"],
        },
    )

    updated_ue = client.get(f"{url}{ue["id"]}").json["data"]
    assert response.status_code == 204
    assert response.data == b""
    assert updated_ue["id"] == ue["id"]
    assert updated_ue["nome"] == "Updated"
    assert updated_ue["codigo"] == ue["codigo"]
    assert updated_ue["abreviacao"] == ue["abreviacao"]


def test_update_nonexistent_ue(client):
    """Test updating a non-existent UE fails."""
    non_existent_id = 9999
    data = make_ue_data()

    response = client.put(f"{url}{non_existent_id}", json=data)

    assert response.status_code == 404
    assert response.json["message"] == "Nenhum registro encontrado."


@pytest.mark.dependency(depends=["create_ue"])
def test_update_ue_with_existing_codigo(client):
    """Test updating a UE with a codigo fails."""

    # Create two UEs
    data1 = {"nome": "UE One", "codigo": "1111", "abreviacao": "UT1"}
    data2 = {"nome": "UE Two", "codigo": "2222", "abreviacao": "UT2"}

    ue1 = create_ue(client, data=data1).json["data"]
    ue2 = create_ue(client, data=data2).json["data"]

    # Attempt to update UE2 with UE1's codigo
    ue2["codigo"] = ue1["codigo"]
    response = client.put(
        f"{url}{ue2["id"]}",
        json={"nome": "Update nome", "codigo": ue1["codigo"], "abreviacao": "UT2"},
    )
    print(response)

    assert response.status_code == 422
    assert response.json["message"] == "Já existe uma UE com esse código."


@pytest.mark.dependency(depends=["create_ue"])
def test_delete_existing_ue(client):
    """Test deleting an existing UE is successful."""

    # Create a UE
    ue = create_ue(client).json["data"]

    # Delete the created UE
    response = client.delete(f"{url}{ue["id"]}")

    assert response.status_code == 204
    assert response.data == b""

    # Try retrieving it to confirm deletion
    get_response = client.get(f"{url}{ue["id"]}")
    assert get_response.status_code == 404


def test_delete_nonexistent_ue(client):
    """Test deleting a non-existent UE fails."""

    non_existent_id = 9999
    response = client.delete(f"{url}{non_existent_id}")

    assert response.status_code == 404
    assert response.json["message"] == "Nenhum registro encontrado."


#


def make_ue_data() -> dict:
    """Make an object of data for body requests."""
    return {"nome": "UE Test", "codigo": "1234", "abreviacao": "UT"}


def create_ue(client, data=make_ue_data()) -> dict:
    """Create an entry in the database."""
    return client.post(url, json=data)
