"""Testes unitários básicos para o cliente da API IBGE e o processamento de dados."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.services import data_processing as dp
from app.services import ibge_api


def test_get_rendimento_medio_por_uf_returns_data():
    data = ibge_api.get_rendimento_medio_por_uf()
    assert isinstance(data, list)
    assert len(data) > 1  # cabeçalho + linhas


def test_get_rendimento_medio_por_setor_uf_returns_data():
    data = ibge_api.get_rendimento_medio_por_setor_uf()
    assert isinstance(data, list)
    assert len(data) > 1


def test_build_rendimento_uf_dataframe():
    raw = ibge_api.get_rendimento_medio_por_uf()
    df = dp.build_rendimento_uf_dataframe(raw)
    assert not df.empty
    assert set(["sigla", "nome", "regiao", "rendimento_medio", "faixa_cor"]).issubset(df.columns)
    assert df["sigla"].nunique() == len(df)  # sem UF duplicada


def test_build_top_setores_por_uf():
    raw_setor = ibge_api.get_rendimento_medio_por_setor_uf()
    top = dp.build_top_setores_por_uf(raw_setor, top_n=3)
    assert isinstance(top, dict)
    assert "SP" in top
    assert len(top["SP"]) <= 3
    # deve estar ordenado do maior para o menor
    valores = [item["valor"] for item in top["SP"]]
    assert valores == sorted(valores, reverse=True)


def test_faixa_cor_para_valor():
    assert dp.faixa_cor_para_valor(2800) == "#DCEBFB"
    assert dp.faixa_cor_para_valor(6500) == "#0B3C82"


def test_compute_summary_metrics():
    raw = ibge_api.get_rendimento_medio_por_uf()
    df = dp.build_rendimento_uf_dataframe(raw)
    summary = dp.compute_summary_metrics(df)
    assert summary["media_brasil"] > 0
    assert summary["maior_uf"]["valor"] >= summary["menor_uf"]["valor"]
