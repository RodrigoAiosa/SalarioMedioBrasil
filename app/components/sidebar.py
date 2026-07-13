"""Componente de sidebar com filtros da aplicação."""
from __future__ import annotations

import streamlit as st


def render_sidebar() -> dict:
    """
    Renderiza os controles laterais e retorna um dicionário de filtros
    selecionados pelo usuário.
    """
    with st.sidebar:
        st.markdown("### ⚙️ Filtros")

        periodo_label = st.selectbox(
            "Período de referência",
            options=["Último trimestre disponível"],
            index=0,
            help="A API SIDRA permite consultar trimestres específicos; "
            "por padrão exibimos sempre o mais recente disponível ('last').",
        )

        regioes = st.multiselect(
            "Filtrar por região",
            options=["Norte", "Nordeste", "Centro-Oeste", "Sudeste", "Sul"],
            default=[],
            help="Deixe vazio para mostrar todas as regiões.",
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
        "periodo": periodo_label,
        "regioes": regioes or None,
    }
