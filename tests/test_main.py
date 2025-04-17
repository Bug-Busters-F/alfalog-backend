import pytest
from flask import jsonify
from faker import Faker
from src.exportacoes.model import ExportacaoModel
from src.ufs.model import UFModel
from tests.test_exportacoes import (
    create_exportacao_db,
    create_exportacao_dependencies,
    make_exportacao_data,
)
from tests.test_ufs import create_uf_db

fake = Faker("pt_BR")


class TestValorAgregadoRoute:
    url = "/api/exportacoes/valor-agregado"

    def test_successful_calculation(self, client, session):
        """Test that returns correct valor_agregado calculation in descending order."""

        trans1 = create_exportacao_db(session)
        trans2 = create_exportacao_db(session)
        trans3 = create_exportacao_db(session)
        trans2.ano = trans1.ano
        trans2.uf = trans1.uf
        trans3.ano = trans1.ano
        trans3.uf = trans1.uf
        print(trans1.ano, trans1.uf.id)
        print(trans2.ano, trans2.uf.id)
        print(trans3.ano, trans3.uf.id)
        session.commit()

        response = client.post(
            self.url, json={"uf_id": trans1.uf.id, "ano": trans1.ano}
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
            assert result["id"] > 0
            assert result["valor_agregado"] > 0
            assert result["quantidade"] > 0
            assert result["peso"] > 0
            assert result["valor"] > 0
            assert result["uf_id"] > 0

    def test_no_transactions_found(self, client, session):
        """Test when no transactions exist for the given filters"""
        from tests.test_ufs import create_uf_db

        uf = create_uf_db(session)

        response = client.post(self.url, json={"uf_id": uf.id, "ano": 2025})

        assert response.status_code == 200
        assert response.json == []

    def test_missing_required_parameters(self, client):
        """Test error handling for missing parameters"""
        # Missing uf_id
        response = client.post(self.url, json={"ano": 2025})
        assert response.status_code == 400

        # Missing ano
        response = client.post(self.url, json={"uf_id": 1})
        assert response.status_code == 400

        # Missing both
        response = client.post(self.url, json={})
        assert response.status_code == 400

    def test_filter_by_year(self, client, session):
        """Test that year filter works correctly"""
        trans1 = create_exportacao_db(session)
        trans2 = create_exportacao_db(session)
        trans2.uf = trans1.uf
        trans1.ano = 2024
        trans2.ano = 2025

        session.commit()

        response = client.post(
            self.url, json={"uf_id": trans1.uf.id, "ano": trans1.ano}
        )

        assert response.status_code == 200
        assert len(response.json) == 1
        assert response.json[0]["valor_agregado"] == round(
            trans1.valor / trans1.peso, 2
        )


class TestCargasMovimentadasRoute:
    url = "/api/exportacoes/cargas-movimentadas"

    def test_successful_response(self, client, session):
        """Test successful response with correct sorting"""
        # Setup test data
        uf = UFModel(codigo="35", nome="São Paulo", sigla="SP", nome_regiao="Sudeste")
        session.add(uf)

        trans1 = create_exportacao_db(session)
        trans2 = create_exportacao_db(session)
        trans3 = create_exportacao_db(session)
        trans2.ano = trans1.ano
        trans2.uf = trans1.uf
        trans3.ano = trans1.ano
        trans3.uf = trans1.uf
        print(trans1.ano, trans1.uf.id)
        print(trans2.ano, trans2.uf.id)
        print(trans3.ano, trans3.uf.id)
        session.commit()

        response = client.post(
            self.url, json={"uf_id": trans1.uf.id, "ano": trans1.ano}
        )

        assert response.status_code == 200
        results = response.json
        assert len(results) == 3
        assert results[0]["peso"] >= results[1]["peso"] >= results[2]["peso"]

        for result in results:
            assert "id" in result
            assert "peso" in result
            assert "ncm_id" in result
            assert isinstance(result["peso"], (int, float))
            assert isinstance(result["ncm_id"], int)

    def test_empty_result(self, client, session):
        """Test when no transactions exist for filters"""

        uf = create_uf_db(session)

        response = client.post(self.url, json={"uf_id": uf.id, "ano": 2025})

        assert response.status_code == 200
        assert response.json == []

    def test_missing_parameters(self, client):
        """Test error handling for missing parameters"""
        # Missing uf_id
        response = client.post(self.url, json={"ano": 2025})
        assert response.status_code == 400

        # Missing ano
        response = client.post(self.url, json={"uf_id": 1})
        assert response.status_code == 400

        # Missing both
        response = client.post(self.url, json={})
        assert response.status_code == 400

    def test_filter_by_year(self, client, session):
        """Test that year filter works correctly."""
        trans1 = create_exportacao_db(session)
        trans2 = create_exportacao_db(session)
        trans2.uf = trans1.uf
        trans1.ano = 2024
        trans2.ano = 2025

        session.commit()

        response = client.post(
            self.url, json={"uf_id": trans1.uf.id, "ano": trans1.ano}
        )

        assert response.status_code == 200
        assert len(response.json) == 1
