"""Componente do mapa coroplético (Plotly) do Brasil por rendimento médio."""
from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go

from app.config.settings import CUSTOM_COLORSCALE, FAIXAS_SALARIO


def render_choropleth_map(
    df: pd.DataFrame,
    geojson: dict,
    hover_text: pd.Series,
) -> go.Figure:
    """
    Constrói o mapa coroplético do Brasil, colorido pela faixa de rendimento
    médio, com hover customizado mostrando o Top 3 de setores por UF.
    """
    fig = go.Figure(
        go.Choropleth(
            geojson=geojson,
            locations=df["sigla"],
            z=df["rendimento_medio"],
            featureidkey="id",
            colorscale=CUSTOM_COLORSCALE,
            zmin=FAIXAS_SALARIO[0]["min"],
            zmax=FAIXAS_SALARIO[-1]["max"],
            marker_line_color="white",
            marker_line_width=1.2,
            text=hover_text,
            hovertemplate="%{text}<extra></extra>",
            colorbar=dict(
                title="R$ / mês",
                thickness=14,
                len=0.75,
                tickformat=",.0f",
            ),
        )
    )

    fig.update_geos(
        scope="south america",
        fitbounds="locations",
        visible=False,
        bgcolor="rgba(0,0,0,0)",
    )

    fig.update_layout(
        margin=dict(l=0, r=0, t=10, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=650,
        font=dict(family="Arial, sans-serif", size=13, color="#0B1F3A"),
    )

    return fig
