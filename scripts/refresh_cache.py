#!/usr/bin/env python3
"""
Script utilitário para atualizar manualmente o cache local (data/cache/*.json)
a partir da API SIDRA real, quando executado em um ambiente com acesso à internet.

Uso:
    python scripts/refresh_cache.py

Isso é útil para:
  - Gerar uma "foto" recente dos dados antes de um deploy sem depender
    da API em tempo real (reduz risco de indisponibilidade em produção).
  - Atualizar o fallback local usado quando a API estiver fora do ar.

O cache é gravado automaticamente pelo próprio cliente (app.services.ibge_api)
sempre que uma chamada é bem-sucedida — este script apenas força essas chamadas.
"""
from __future__ import annotations

import logging
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.services import ibge_api

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def main() -> int:
    logger.info("Atualizando cache: rendimento médio por UF (Tabela SIDRA 6407)...")
    try:
        data_uf = ibge_api.get_rendimento_medio_por_uf()
        logger.info("OK — %d registros (incluindo cabeçalho).", len(data_uf))
    except ibge_api.IBGEAPIError as exc:
        logger.error("Falha ao atualizar cache de rendimento por UF: %s", exc)
        return 1

    logger.info("Atualizando cache: rendimento médio por UF e setor (Tabela SIDRA 5436)...")
    try:
        data_setor = ibge_api.get_rendimento_medio_por_setor_uf()
        logger.info("OK — %d registros (incluindo cabeçalho).", len(data_setor))
    except ibge_api.IBGEAPIError as exc:
        logger.error("Falha ao atualizar cache de rendimento por setor: %s", exc)
        return 1

    logger.info("Atualizando cache: série histórica nacional (rendimento médio)...")
    try:
        data_historico = ibge_api.get_serie_historica_rendimento_brasil()
        logger.info("OK — %d registros (incluindo cabeçalho).", len(data_historico))
    except ibge_api.IBGEAPIError as exc:
        logger.error("Falha ao atualizar cache de série histórica: %s", exc)
        return 1

    logger.info("Atualizando cache: metadados de estados...")
    try:
        estados = ibge_api.get_estados_metadata()
        logger.info("OK — %d estados.", len(estados))
    except ibge_api.IBGEAPIError as exc:
        logger.error("Falha ao atualizar metadados de estados: %s", exc)
        return 1

    logger.info("Cache local atualizado com sucesso em data/cache/.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
