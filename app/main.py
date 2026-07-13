"""
Dashboard: Salário Médio da População por Estado no Brasil
Fonte dos dados: PNAD Contínua (IBGE) via API SIDRA.

Execução:
    streamlit run app/main.py
"""
from __future__ import annotations

import logging
import sys
from pathlib import Path

import streamlit as st

# Garante que o pacote `app` seja importável quando executado via
# `streamlit run app/main.py` a partir da raiz do projeto.
sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.components.map_view import render_choropleth_map
from app.components.metrics import render_summary_metrics
from app.components.sidebar import render_sidebar
from app.config.settings import APP_TITLE, CSS_PATH, FONTE_LABEL
from app.services import data_processing as dp
from app.services import ibge_api
from app.utils.formatting import format_brl
from app.utils.geo import load_uf_geojson

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

st.set_page_config(
    page_title="Salário Médio por Estado — Brasil",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)


def _inject_css() -> None:
    if CSS_PATH.exists():
        st.markdown(f"<style>{CSS_PATH.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)


@st.cache_data(ttl=21600, show_spinner=False)
def load_data() -> tuple:
    """Busca e processa todos os dados necessários (com cache de 6h)."""
    raw_rendimento_uf = ibge_api.get_rendimento_medio_por_uf()
    raw_rendimento_setor = ibge_api.get_rendimento_medio_por_setor_uf()
    geojson = load_uf_geojson()

    df = dp.build_rendimento_uf_dataframe(raw_rendimento_uf)
    top_setores = dp.build_top_setores_por_uf(raw_rendimento_setor, top_n=3)
    hover_text = dp.build_hover_text(df, top_setores)
    summary = dp.compute_summary_metrics(df)

    return df, top_setores, hover_text, geojson, summary


def render_header() -> None:
    st.markdown(
        """
        <div class="app-title">
            <span class="black-part">SALÁRIO</span><span class="blue-part">MÉDIO</span>
        </div>
        <div class="app-subtitle">
            DA POPULAÇÃO POR ESTADO NO <span class="highlight">BRASIL</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_legend() -> None:
    from app.config.settings import FAIXAS_SALARIO

    items_html = "".join(
        f"""
        <div class="legend-item">
            <div class="legend-swatch" style="background:{f['cor']};"></div>
            <span>{f['label']}</span>
        </div>
        """
        for f in FAIXAS_SALARIO
    )
    st.markdown(
        f"""
        <div class="legend-box">
            <b>Renda Média Mensal</b><br><br>
            {items_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_media_brasil_card(media_brasil: float | None) -> None:
    st.markdown(
        f"""
        <div class="media-brasil-card">
            <div class="label">MÉDIA BRASIL</div>
            <div class="value">{format_brl(media_brasil)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    _inject_css()
    render_header()

    filters = render_sidebar()

    with st.spinner("Carregando dados da PNAD Contínua (IBGE)..."):
        try:
            df, top_setores, hover_text, geojson, summary = load_data()
        except ibge_api.IBGEAPIError as exc:
            st.error(
                "Não foi possível carregar os dados do IBGE no momento, "
                "e nenhum cache local foi encontrado.\n\n"
                f"Detalhe técnico: {exc}"
            )
            st.stop()

    if df.empty:
        st.warning("Nenhum dado de rendimento por UF foi retornado pela API.")
        st.stop()

    # Aplica filtro de região, se selecionado
    df_filtered = df
    if filters.get("regioes"):
        df_filtered = df[df["regiao"].isin(filters["regioes"])].reset_index(drop=True)
        hover_text_filtered = hover_text.loc[df_filtered.index]
    else:
        hover_text_filtered = hover_text

    render_summary_metrics(summary)
    st.write("")

    col_map, col_side = st.columns([3, 1])

    with col_map:
        st.plotly_chart(
            render_choropleth_map(df_filtered, geojson, hover_text_filtered),
            use_container_width=True,
            config={"displayModeBar": False},
        )
        st.caption("💡 Passe o mouse sobre um estado para ver o Top 3 de setores com maior média salarial.")

    with col_side:
        render_legend()
        st.write("")
        render_media_brasil_card(summary["media_brasil"])

    with st.expander("📊 Ver tabela completa de dados por estado"):
        st.dataframe(
            df[["sigla", "nome", "regiao", "rendimento_medio", "faixa_label"]].rename(
                columns={
                    "sigla": "UF",
                    "nome": "Estado",
                    "regiao": "Região",
                    "rendimento_medio": "Rendimento Médio (R$)",
                    "faixa_label": "Faixa",
                }
            ),
            use_container_width=True,
            hide_index=True,
        )

    st.markdown(f'<div class="footer-note">{FONTE_LABEL}</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()
