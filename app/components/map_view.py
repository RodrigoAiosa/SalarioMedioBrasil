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
    # Usa o range real dos dados (não o teto "catch-all" da última faixa,
    # que é 99999 e esmagaria toda a escala de cores).
    valor_min = float(df["rendimento_medio"].min())
    valor_max = float(df["rendimento_medio"].max())

    fig = go.Figure(
        go.Choropleth(
            geojson=geojson,
            locations=df["sigla"],
            z=df["rendimento_medio"],
            featureidkey="id",
            colorscale=CUSTOM_COLORSCALE,
            zmin=valor_min,
            zmax=valor_max,
            marker_line_color="#0B1220",
            marker_line_width=1,
            text=hover_text,
            hovertemplate="%{text}<extra></extra>",
            colorbar=dict(
                title=dict(text="R$ / mês", font=dict(color="#E7EEF9")),
                thickness=14,
                len=0.75,
                tickformat=",.0f",
                tickfont=dict(color="#E7EEF9"),
                outlinewidth=0,
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
        font=dict(family="Arial, sans-serif", size=13, color="#E7EEF9"),
        hoverlabel=dict(
            bgcolor="#111C33",
            font_color="#E7EEF9",
            font_size=13,
            bordercolor="#1E6FD9",
        ),
    )

    return fig
