## Tests for Transacao Collection

from typing import Any, Callable
import pytest

from tests.test_ncms import create_ncm
from tests.test_ues import create_ue
from tests.test_paises import create_pais
from tests.test_ufs import create_uf
from tests.test_vias import create_via
from tests.test_urfs import create_urf


url = "/api/transacoes/"


def test_get_transacoes_empty(client):
    """Test Retrieve all entries when database is empty is successful."""
    response = client.get(url)
    assert response.status_code == 200
    assert response.json == []


@pytest.mark.dependency(
    name="create_transacao",
    depends=["create_ncm"],
    scope="package",
)
def test_create_transacao(client) -> int:
    """Test Create a new valid entry is successful."""
    dep = create_transacao_dependencies(client)
    response = create_transacao(client, dep=lambda client: dep)

    assert response.status_code == 201
    assert "id" in response.json["data"]
    assert response.json["data"]["codigo"] == "1234"
    assert response.json["data"]["nome"] == "Transacao Test"
    assert response.json["data"]["ano"] == 2025
    assert response.json["data"]["mes"] == 3
    assert response.json["data"]["quantidade"] == 30
    assert response.json["data"]["peso"] == 42
    assert response.json["data"]["valor"] == 123
    assert response.json["data"]["ncm_id"] == dep["ncm"]["id"]
    assert response.json["data"]["ue_id"] == dep["ue"]["id"]
    assert response.json["data"]["pais_id"] == dep["pais"]["id"]
    assert response.json["data"]["uf_id"] == dep["uf"]["id"]
    assert response.json["data"]["via_id"] == dep["via"]["id"]
    assert response.json["data"]["urf_id"] == dep["urf"]["id"]


@pytest.mark.dependency(depends=["create_transacao", "create_ncm"], scope="package")
def test_get_transacoes_with_data(client):
    """Test Retrieve all entries when database has data is successful."""
    dep = create_transacao_dependencies(client)
    create_transacao(client, dep=lambda client: dep)

    # Retrieve all Transacoes
    response = client.get(url)

    assert response.status_code == 200
    assert isinstance(response.json, list)
    assert len(response.json) > 0
    assert any(
        transacao["data"]["nome"] == "Transacao Test"
        and transacao["data"]["codigo"] == "1234"
        and transacao["data"]["nome"] == "Transacao Test"
        and transacao["data"]["ano"] == 2025
        and transacao["data"]["mes"] == 3
        and transacao["data"]["quantidade"] == 30
        and transacao["data"]["peso"] == 42
        and transacao["data"]["valor"] == 123
        and transacao["data"]["ncm_id"] == dep["ncm"]["id"]
        and transacao["data"]["ue_id"] == dep["ue"]["id"]
        and transacao["data"]["pais_id"] == dep["pais"]["id"]
        and transacao["data"]["uf_id"] == dep["uf"]["id"]
        and transacao["data"]["via_id"] == dep["via"]["id"]
        and transacao["data"]["urf_id"] == dep["urf"]["id"]
        for transacao in response.json
    )


@pytest.mark.dependency(depends=["create_ncm"], scope="package")
def test_create_duplicate_transacao(client):
    """Test Create an entry with an existing codigo fails."""
    dep = create_transacao_dependencies(client)
    create_transacao(client, dep=lambda client: dep)
    response = create_transacao(client, dep=lambda client: dep)

    assert response.status_code == 422
    assert response.json["message"] == "Já existe uma Transacao com esse código."


@pytest.mark.dependency(depends=["create_ncm"], scope="package")
@pytest.mark.parametrize(
    "payload, missing_field",
    [
        ({"codigo": "1234"}, "nome"),
        ({"nome": "Transacao Test"}, "codigo"),
        ({}, "nome"),
    ],
)
def test_create_transacao_missing_fields(client, payload, missing_field):
    """Test Create an entry with missing nome or codigo fails."""

    response = create_transacao(client, data=lambda dep: payload)

    assert response.status_code == 400
    assert "message" in response.json
    assert missing_field in response.json["message"]


## Tests for Transacao
@pytest.mark.dependency(
    name="get_transacao",
    depends=["create_transacao", "create_ncm"],
    scope="package",
)
def test_get_existing_transacao(client):
    """
    Test Retrieve a valid entry by ID is successful.
    Depends on test_create_transacao.
    """
    dep = create_transacao_dependencies(client)
    transacao = create_transacao(client, dep=lambda client: dep).json["data"]

    response = client.get(f"{url}{transacao["id"]}")

    assert response.status_code == 200
    assert response.json["data"]["id"] == transacao["id"]
    assert response.json["data"]["nome"] == "Transacao Test"
    assert response.json["data"]["codigo"] == "1234"
    assert response.json["data"]["ano"] == 2025
    assert response.json["data"]["mes"] == 3
    assert response.json["data"]["quantidade"] == 30
    assert response.json["data"]["peso"] == 42
    assert response.json["data"]["valor"] == 123
    assert response.json["data"]["ncm_id"] == dep["ncm"]["id"]
    assert response.json["data"]["ue_id"] == dep["ue"]["id"]
    assert response.json["data"]["pais_id"] == dep["pais"]["id"]
    assert response.json["data"]["uf_id"] == dep["uf"]["id"]
    assert response.json["data"]["via_id"] == dep["via"]["id"]
    assert response.json["data"]["urf_id"] == dep["urf"]["id"]


def test_get_nonexistent_transacao(client):
    """Test Retrieve a non-existent entry is successful."""
    response = client.get(f"{url}999")

    assert response.status_code == 404
    assert response.json["message"] == "Nenhum registro encontrado."


@pytest.mark.dependency(depends=["create_transacao", "get_transacao"])
def test_update_transacao_with_different_codigo(client):
    """
    Test Update an existing entry with a different codigo is successful.
    Depends on test_create_transacao and test_get_existing_transacao.
    """
    dep = create_transacao_dependencies(client)
    transacao = create_transacao(client, dep=lambda client: dep).json["data"]

    response = client.put(
        f"{url}{transacao['id']}",
        json={
            "nome": "Updated",
            "codigo": "5678",
            "ano": transacao["ano"],
            "mes": transacao["mes"],
            "quantidade": transacao["quantidade"],
            "peso": transacao["peso"],
            "valor": transacao["valor"],
            "ncm_id": transacao["ncm_id"],
            "ue_id": transacao["ue_id"],
            "pais_id": transacao["pais_id"],
            "uf_id": transacao["uf_id"],
            "via_id": transacao["via_id"],
            "urf_id": transacao["urf_id"],
        },
    )

    updated_transacao = client.get(f"{url}{transacao["id"]}").json["data"]

    assert response.status_code == 204
    assert response.data == b""
    assert updated_transacao["id"] == transacao["id"]
    assert updated_transacao["nome"] == "Updated"
    assert updated_transacao["codigo"] == "5678"
    assert updated_transacao["ano"] == 2025
    assert updated_transacao["mes"] == 3
    assert updated_transacao["quantidade"] == 30
    assert updated_transacao["peso"] == 42
    assert updated_transacao["valor"] == 123
    assert updated_transacao["ncm_id"] == dep["ncm"]["id"]
    assert updated_transacao["ue_id"] == dep["ue"]["id"]
    assert updated_transacao["pais_id"] == dep["pais"]["id"]
    assert updated_transacao["uf_id"] == dep["uf"]["id"]
    assert updated_transacao["via_id"] == dep["via"]["id"]
    assert updated_transacao["urf_id"] == dep["urf"]["id"]


@pytest.mark.dependency(depends=["create_transacao", "get_transacao"])
def test_update_transacao_with_same_codigo(client):
    """
    Test Update an existing entry with the original codigo is successful.
    Depends on test_create_transacao and test_get_existing_transacao.
    """
    dep = create_transacao_dependencies(client)
    transacao = create_transacao(client, dep=lambda client: dep).json["data"]

    response = client.put(
        f"{url}{transacao['id']}",
        json={
            "nome": "Updated",
            "codigo": "1234",
            "ano": transacao["ano"],
            "mes": transacao["mes"],
            "quantidade": transacao["quantidade"],
            "peso": transacao["peso"],
            "valor": transacao["valor"],
            "ncm_id": transacao["ncm_id"],
            "ue_id": transacao["ue_id"],
            "pais_id": transacao["pais_id"],
            "uf_id": transacao["uf_id"],
            "via_id": transacao["via_id"],
            "urf_id": transacao["urf_id"],
        },
    )

    updated_transacao = client.get(f"{url}{transacao["id"]}").json["data"]
    assert response.status_code == 204
    assert response.data == b""
    assert updated_transacao["id"] == transacao["id"]
    assert updated_transacao["nome"] == "Updated"
    assert updated_transacao["codigo"] == "1234"
    assert updated_transacao["ano"] == 2025
    assert updated_transacao["mes"] == 3
    assert updated_transacao["quantidade"] == 30
    assert updated_transacao["peso"] == 42
    assert updated_transacao["valor"] == 123
    assert updated_transacao["ncm_id"] == dep["ncm"]["id"]
    assert updated_transacao["ue_id"] == dep["ue"]["id"]
    assert updated_transacao["pais_id"] == dep["pais"]["id"]
    assert updated_transacao["uf_id"] == dep["uf"]["id"]
    assert updated_transacao["via_id"] == dep["via"]["id"]
    assert updated_transacao["urf_id"] == dep["urf"]["id"]


def test_update_nonexistent_transacao(client):
    """Test updating a non-existent Transacao fails."""
    non_existent_id = 9999
    dep = create_transacao_dependencies(client)
    data = make_transacao_data(dep)

    response = client.put(f"{url}{non_existent_id}", json=data)

    assert response.status_code == 404
    assert response.json["message"] == "Nenhum registro encontrado."


@pytest.mark.dependency(depends=["create_transacao"])
def test_update_transacao_with_existing_codigo(client):
    """Test updating a Transacao with a codigo fails."""

    # Create two Transacoes
    dep = create_transacao_dependencies(client)

    def data1(dep):
        data = make_transacao_data(dep)
        data["nome"] = "Transacao One"
        data["codigo"] = "1111"
        return data

    def data2(dep):
        data = make_transacao_data(dep)
        data["nome"] = "Transacao Two"
        data["codigo"] = "2222"
        return data

    transacao1 = create_transacao(client, data=data1, dep=lambda client: dep).json[
        "data"
    ]
    transacao2 = create_transacao(client, data=data2, dep=lambda client: dep).json[
        "data"
    ]

    # Attempt to update Transacao2 with Transacao1's codigo
    transacao2["codigo"] = transacao1["codigo"]
    response = client.put(f"{url}{transacao2["id"]}", json=transacao2)

    assert response.status_code == 422
    assert response.json["message"] == "Já existe uma Transacao com esse código."


@pytest.mark.dependency(depends=["create_transacao"])
def test_delete_existing_transacao(client):
    """Test deleting an existing Transacao is successful."""

    # Create a Transacao
    transacao = create_transacao(client).json["data"]

    # Delete the created Transacao
    response = client.delete(f"{url}{transacao["id"]}")

    assert response.status_code == 204
    assert response.data == b""

    # Try retrieving it to confirm deletion
    get_response = client.get(f"{url}{transacao["id"]}")
    assert get_response.status_code == 404


def test_delete_nonexistent_transacao(client):
    """Test deleting a non-existent Transacao fails."""

    non_existent_id = 9999
    response = client.delete(f"{url}{non_existent_id}")

    assert response.status_code == 404
    assert response.json["message"] == "Nenhum registro encontrado."


#


def make_transacao_data(dep: dict) -> dict:
    """Make an object of Transacao for body requests."""
    return {
        "codigo": "1234",
        "nome": "Transacao Test",
        "ano": "2025",
        "mes": "03",
        "quantidade": "30",
        "peso": "42",
        "valor": "123",
        "ncm_id": dep["ncm"]["id"],
        "ue_id": dep["ue"]["id"],
        "pais_id": dep["pais"]["id"],
        "uf_id": dep["uf"]["id"],
        "via_id": dep["via"]["id"],
        "urf_id": dep["urf"]["id"],
    }


def create_transacao_dependencies(client) -> dict:
    """Create all the dependencies of Transacao."""
    return {
        "ncm": create_ncm(client).json["data"],
        "ue": create_ue(client).json["data"],
        "pais": create_pais(client).json["data"],
        "uf": create_uf(client).json["data"],
        "via": create_via(client).json["data"],
        "urf": create_urf(client).json["data"],
    }


def create_transacao(
    client,
    data: Callable[[dict], dict] = make_transacao_data,
    dep: Callable[[Any], dict] = create_transacao_dependencies,
) -> dict:
    """Create a Transacao instance.

    Args:
        client (_type_): _description_
        data (Callable, optional): If data is passed, it is invoked to create the request body data. Otherwise, a default body will be create and `dep` will be included in it.
        dep (Callable, optional): If data is not passed, this will be invoked to create

    Raises:
        Exception: _description_

    Returns:
        dict: HTTP response

    """
    depend = dep(client)
    bodyData = data(depend)
    return client.post(url, json=bodyData)
