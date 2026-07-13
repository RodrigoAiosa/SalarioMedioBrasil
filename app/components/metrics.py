"""Componente de cards de métricas resumo (média Brasil, maior/menor UF)."""
from __future__ import annotations

import streamlit as st

from app.utils.formatting import format_brl


def render_summary_metrics(summary: dict) -> None:
    """Renderiza 3 cards de métricas no topo do dashboard."""
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            label="🇧🇷 Média Brasil",
            value=format_brl(summary["media_brasil"]),
        )

    with col2:
        maior = summary.get("maior_uf")
        if maior:
            st.metric(
                label=f"🔼 Maior média — {maior['sigla']}",
                value=format_brl(maior["valor"]),
                help=maior["nome"],
            )

    with col3:
        menor = summary.get("menor_uf")
        if menor:
            st.metric(
                label=f"🔽 Menor média — {menor['sigla']}",
                value=format_brl(menor["valor"]),
                help=menor["nome"],
            )
