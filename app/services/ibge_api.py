"""
Cliente para as APIs públicas do IBGE:
  - API SIDRA (dados agregados da PNAD Contínua)
  - API de Localidades (malha geográfica / metadados de UF)

Referência de documentação: https://servicodados.ibge.gov.br/api/docs/
                             https://apisidra.ibge.gov.br/

O cliente tenta sempre a chamada real à API. Se a chamada falhar
(rede indisponível, timeout, erro 5xx, etc.) e USE_LOCAL_CACHE_FALLBACK
estiver habilitado, ele recorre a um arquivo de cache local em disco
(data/cache/*.json), garantindo que o dashboard nunca quebre em ambientes
com acesso restrito à internet.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

import requests
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from app.config.settings import (
    CACHE_DIR,
    ENDPOINTS,
    REQUEST_TIMEOUT,
    USE_LOCAL_CACHE_FALLBACK,
)

logger = logging.getLogger(__name__)

_RETRYABLE_EXCEPTIONS = (
    requests.exceptions.ConnectionError,
    requests.exceptions.Timeout,
    requests.exceptions.HTTPError,
)


class IBGEAPIError(Exception):
    """Erro genérico ao consultar a API do IBGE (sem fallback disponível)."""


def _cache_path(name: str) -> Path:
    return CACHE_DIR / f"{name}.json"


def _read_cache(name: str) -> Any | None:
    path = _cache_path(name)
    if not path.exists():
        return None
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except (json.JSONDecodeError, OSError) as exc:
        logger.warning("Falha ao ler cache local %s: %s", path, exc)
        return None


def _write_cache(name: str, payload: Any) -> None:
    path = _cache_path(name)
    try:
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, ensure_ascii=False, indent=2)
    except OSError as exc:
        logger.warning("Falha ao gravar cache local %s: %s", path, exc)


@retry(
    reraise=True,
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=6),
    retry=retry_if_exception_type(_RETRYABLE_EXCEPTIONS),
)
def _get_json(url: str) -> Any:
    response = requests.get(url, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    return response.json()


def _fetch_with_fallback(url: str, cache_name: str) -> Any:
    """Busca `url`; em caso de falha, usa cache local; grava cache em caso de sucesso."""
    try:
        data = _get_json(url)
        _write_cache(cache_name, data)
        return data
    except Exception as exc:  # noqa: BLE001 - queremos capturar qualquer falha de rede/parse
        logger.warning("Falha ao consultar API IBGE (%s): %s", url, exc)
        if USE_LOCAL_CACHE_FALLBACK:
            cached = _read_cache(cache_name)
            if cached is not None:
                logger.info("Usando cache local para %s", cache_name)
                return cached
        raise IBGEAPIError(
            f"Não foi possível obter dados de {url} e nenhum cache local foi encontrado."
        ) from exc


def get_rendimento_medio_por_uf(periodo: str = "last") -> list[dict]:
    """
    Retorna o rendimento médio mensal por UF (Tabela SIDRA 6407).

    Estrutura de retorno bruta da API SIDRA: lista de dicts, sendo o
    primeiro item o cabeçalho (descrição das colunas) e os demais os
    valores por UF.
    """
    url = ENDPOINTS.rendimento_uf(periodo)
    return _fetch_with_fallback(url, cache_name="rendimento_uf")


def get_rendimento_medio_por_setor_uf(periodo: str = "last") -> list[dict]:
    """
    Retorna o rendimento médio mensal por UF e Grupamento de atividade
    (Tabela SIDRA 5436) — usado para calcular o Top 3 de setores por estado.
    """
    url = ENDPOINTS.rendimento_setor_uf(periodo)
    return _fetch_with_fallback(url, cache_name="rendimento_setor_uf")


def get_serie_historica_rendimento_brasil(periodo: str = "all") -> list[dict]:
    """
    Retorna a série histórica (nível Brasil) do rendimento médio mensal
    (Tabela SIDRA 6407, nível territorial N1). Usada na aba de Histórico
    para exibir a tabela de Período x Variação (%MoM/%QoQ e %YoY).
    """
    url = ENDPOINTS.rendimento_historico_brasil(periodo)
    return _fetch_with_fallback(url, cache_name="historico_rendimento_brasil")


def get_estados_metadata() -> list[dict]:
    """Retorna metadados oficiais das UFs (API de Localidades do IBGE)."""
    url = ENDPOINTS.estados()
    return _fetch_with_fallback(url, cache_name="estados_metadata")


def get_malha_geojson() -> dict:
    """Retorna o GeoJSON da malha territorial do Brasil (nível UF)."""
    url = ENDPOINTS.malha_uf_geojson()
    return _fetch_with_fallback(url, cache_name="malha_uf")
