import pytest
from faker import Faker

from tests.test_transacoes import create_transacao_db

fake = Faker("pt_BR")


class TestValorAgregadoRoute:
    url = "/api/valor_agregado"

    def test_successful_calculation(self, client, session):
        """Test that returns correct valor_agregado calculation in descending order."""

        trans1 = create_transacao_db(session)
        trans2 = create_transacao_db(session)
        trans3 = create_transacao_db(session)
        trans2.ano = trans1.ano
        trans2.uf = trans1.uf
        trans3.ano = trans1.ano
        trans3.uf = trans1.uf
        print(trans1.ano, trans1.uf.id)
        print(trans2.ano, trans2.uf.id)
        print(trans3.ano, trans3.uf.id)
        session.commit()

        response = client.post(
            "/api/valor_agregado", json={"uf_id": trans1.uf.id, "ano": trans1.ano}
        )
        results = response.json

        assert response.status_code == 200
        assert len(results) == 3
        assert (
            results[0]["valor_agregado"]
            >= results[1]["valor_agregado"]
            >= results[2]["valor_agregado"]
        )

        for result in results:
            assert "id" in result
            assert "valor_agregado" in result
            assert "quantidade" in result
            assert "peso" in result
            assert "valor" in result
            assert "uf_id" in result
