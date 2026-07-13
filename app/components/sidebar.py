"""Componente de sidebar com filtros da aplicação."""
from __future__ import annotations

import streamlit as st

from app.config.settings import (
    ANO_MAIS_RECENTE,
    ANOS_DISPONIVEIS,
    ANOS_HISTORICO_OPCOES,
    ANOS_HISTORICO_PADRAO,
)


def render_sidebar() -> dict:
    """
    Renderiza os controles laterais e retorna um dicionário de filtros
    selecionados pelo usuário.
    """
    with st.sidebar:
        st.markdown("### ⚙️ Filtros")

        ano_selecionado = st.selectbox(
            "📅 Ano de referência",
            options=ANOS_DISPONIVEIS,
            index=0,
            format_func=lambda a: f"{a} (mais recente)" if a == ANO_MAIS_RECENTE else str(a),
            help="Ao selecionar um ano, o mapa, os cards de resumo e o Top 3 de "
            "setores no hover são recalculados para o 4º trimestre daquele ano.",
        )

        regioes = st.multiselect(
            "Filtrar por região (mapa)",
            options=["Norte", "Nordeste", "Centro-Oeste", "Sudeste", "Sul"],
            default=[],
            help="Deixe vazio para mostrar todas as regiões.",
        )

        st.markdown("---")
        anos_historico = st.select_slider(
            "📈 Janela do histórico (aba Histórico)",
            options=ANOS_HISTORICO_OPCOES,
            value=ANOS_HISTORICO_PADRAO,
            help="Define quantos anos para trás a aba Histórico exibe no gráfico e na tabela.",
        )

        st.markdown("---")
        st.markdown("### ℹ️ Sobre")
        st.caption(
            "Dados extraídos da **PNAD Contínua** (IBGE) via **API SIDRA**. "
            "Rendimento médio mensal real de todos os trabalhos, das pessoas "
            "de 14 anos ou mais de idade, ocupadas na semana de referência."
        )
        st.caption("Documentação da API: servicodados.ibge.gov.br/api/docs")

    return {
        "ano": ano_selecionado,
        "regioes": regioes or None,
        "anos_historico": anos_historico,
    }
