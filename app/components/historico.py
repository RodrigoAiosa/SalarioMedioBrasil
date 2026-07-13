"""Componente da aba de Histórico: filtro de período, gráfico de tendência
e tabela de variações %MoM (QoQ) e %YoY do rendimento médio nacional."""
from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from app.utils.formatting import format_brl


def render_historico_chart(df: pd.DataFrame) -> go.Figure:
    """Gráfico de linha da evolução do rendimento médio nacional."""
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df["data_ref"],
            y=df["rendimento_medio"],
            mode="lines+markers",
            line=dict(color="#3B8CF2", width=3, shape="spline"),
            marker=dict(size=5, color="#3B8CF2"),
            fill="tozeroy",
            fillcolor="rgba(59,140,242,0.15)",
            hovertemplate="%{x|%b/%Y}<br>Rendimento médio: R$ %{y:,.2f}<extra></extra>",
        )
    )
    fig.update_layout(
        margin=dict(l=0, r=0, t=10, b=0),
        height=340,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Arial, sans-serif", size=12, color="#B8C4D9"),
        xaxis=dict(showgrid=False, color="#B8C4D9"),
        yaxis=dict(showgrid=True, gridcolor="rgba(184,196,217,0.12)", tickprefix="R$ ", color="#B8C4D9"),
        hovermode="x unified",
        hoverlabel=dict(bgcolor="#111C33", font_color="#E7EEF9", bordercolor="#1E6FD9"),
    )
    return fig


def _fmt_pct(value: float | None) -> str:
    if value is None or pd.isna(value):
        return "—"
    sinal = "+" if value > 0 else ""
    return f"{sinal}{value:.2f}%".replace(".", ",")


def render_historico_tabela(df: pd.DataFrame) -> None:
    """Renderiza a tabela de Período x Rendimento x %MoM(QoQ) x %YoY."""
    tabela = df[["periodo_label", "rendimento_medio", "var_mom", "var_yoy"]].copy()
    tabela = tabela.iloc[::-1]  # período mais recente primeiro
    tabela = tabela.rename(
        columns={
            "periodo_label": "Período (MêsAno)",
            "rendimento_medio": "Rendimento Médio",
            "var_mom": "% QoQ (trim. anterior)",
            "var_yoy": "% YoY (mesmo trim. ano anterior)",
        }
    )

    st.dataframe(
        tabela,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Período (MêsAno)": st.column_config.TextColumn(width="small"),
            "Rendimento Médio": st.column_config.NumberColumn(format="R$ %.2f"),
            "% QoQ (trim. anterior)": st.column_config.NumberColumn(format="%.2f%%"),
            "% YoY (mesmo trim. ano anterior)": st.column_config.NumberColumn(format="%.2f%%"),
        },
    )


def render_historico_tab(df_historico_filtrado: pd.DataFrame, anos_selecionados: int) -> None:
    """Monta a aba completa de Histórico: cards de variação recente, gráfico e tabela."""
    if df_historico_filtrado.empty:
        st.warning("Sem dados históricos disponíveis para o período selecionado.")
        return

    ultimo = df_historico_filtrado.iloc[-1]

    st.markdown(
        f"#### Evolução do rendimento médio nacional — últimos {anos_selecionados} anos "
        f"({df_historico_filtrado.iloc[0]['periodo_label']} a {ultimo['periodo_label']})"
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Rendimento médio (último período)", format_brl(ultimo["rendimento_medio"]))
    with col2:
        st.metric("Variação QoQ (trimestre anterior)", _fmt_pct(ultimo["var_mom"]))
    with col3:
        st.metric("Variação YoY (mesmo trimestre, ano anterior)", _fmt_pct(ultimo["var_yoy"]))

    st.plotly_chart(render_historico_chart(df_historico_filtrado), use_container_width=True, config={"displayModeBar": False})

    st.markdown("##### 📋 Tabela detalhada por período")
    st.caption(
        "A PNAD Contínua divulga rendimento em periodicidade **trimestral**. "
        "A coluna 'Período (MêsAno)' usa o último mês de cada trimestre; "
        "'% QoQ' equivale à variação mês-a-mês solicitada, aplicada ao trimestre "
        "mais recente disponível (não há divulgação mensal deste indicador)."
    )
    render_historico_tabela(df_historico_filtrado)
