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


def test_filtro_por_ano_atualiza_indicadores():
    """Ao trocar o ano de referência, os indicadores (média Brasil, maior/menor UF)
    devem mudar de valor, confirmando que o filtro de ANO afeta os dados carregados."""
    from app.config.settings import periodo_para_ano

    periodo_2024 = periodo_para_ano(2024)
    periodo_2018 = periodo_para_ano(2018)
    assert periodo_2018 == "201804"

    raw_2024 = ibge_api.get_rendimento_medio_por_uf(periodo_2024)
    raw_2018 = ibge_api.get_rendimento_medio_por_uf(periodo_2018)

    df_2024 = dp.build_rendimento_uf_dataframe(raw_2024)
    df_2018 = dp.build_rendimento_uf_dataframe(raw_2018)

    summary_2024 = dp.compute_summary_metrics(df_2024)
    summary_2018 = dp.compute_summary_metrics(df_2018)

    assert summary_2024["media_brasil"] != summary_2018["media_brasil"]
    # 2018 deve ter média menor que 2024 (crescimento real ao longo do tempo)
    assert summary_2018["media_brasil"] < summary_2024["media_brasil"]


def test_hover_text_permanece_alinhado_apos_filtro_regiao():
    """Regressão: ao filtrar por região (mesma lógica usada em main.py, via
    máscara booleana + reset_index em ambos df e hover_text), o hover de cada
    estado deve continuar correspondendo ao estado correto — bug relatado
    anteriormente fazia o hover do Rio de Janeiro mostrar dados do Distrito Federal.
    """
    raw_uf = ibge_api.get_rendimento_medio_por_uf()
    raw_setor = ibge_api.get_rendimento_medio_por_setor_uf()

    df = dp.build_rendimento_uf_dataframe(raw_uf)
    top_setores = dp.build_top_setores_por_uf(raw_setor, top_n=3)
    hover_text = dp.build_hover_text(df, top_setores)

    # Simula o filtro por região "Sudeste" (inclui RJ, SP, MG, ES) como em main.py
    mask = df["regiao"] == "Sudeste"
    df_filtered = df[mask].reset_index(drop=True)
    hover_text_filtered = hover_text[mask].reset_index(drop=True)

    assert len(df_filtered) == len(hover_text_filtered)

    for i, row in df_filtered.iterrows():
        texto = hover_text_filtered.iloc[i]
        assert row["nome"] in texto, (
            f"Desalinhamento detectado: hover na posição {i} (UF={row['sigla']}) "
            f"não contém o nome do estado '{row['nome']}'. Texto: {texto[:120]}"
        )
        # Garante que nenhum outro nome de UF do dataframe completo "vazou" para essa posição
        outras_ufs_sudeste = [n for n in df_filtered["nome"] if n != row["nome"]]
        for outro_nome in outras_ufs_sudeste:
            assert not texto.startswith(f"<b>{outro_nome}"), (
                f"Hover da posição {i} (UF={row['sigla']}) contém dados de outro estado: {outro_nome}"
            )
