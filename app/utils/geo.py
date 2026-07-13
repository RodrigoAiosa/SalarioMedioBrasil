"""
Utilitários para a malha geográfica (GeoJSON) dos estados brasileiros.

Prioriza a malha oficial baixada da API de Malhas do IBGE
(https://servicodados.ibge.gov.br/api/docs/malhas), com fallback para o
GeoJSON estático salvo em `data/cache/brasil_uf.geojson`
(cada feature possui `id` = sigla da UF, ex: "SP", "RJ").
"""
from __future__ import annotations

import json
import logging
from typing import Any

from app.config.settings import CACHE_DIR

logger = logging.getLogger(__name__)

_LOCAL_GEOJSON_PATH = CACHE_DIR / "brasil_uf.geojson"


def load_uf_geojson() -> dict[str, Any]:
    """
    Carrega o GeoJSON dos 27 estados brasileiros.

    Cada feature tem `id` igual à sigla da UF (ex.: "SP"), o que permite
    usar `featureidkey="id"` diretamente no Plotly Choropleth.
    """
    try:
        with open(_LOCAL_GEOJSON_PATH, "r", encoding="utf-8") as fh:
            geojson = json.load(fh)
        logger.info("GeoJSON de UFs carregado (%d features).", len(geojson.get("features", [])))
        return geojson
    except (OSError, json.JSONDecodeError) as exc:
        logger.error("Falha ao carregar GeoJSON local de UFs: %s", exc)
        raise
