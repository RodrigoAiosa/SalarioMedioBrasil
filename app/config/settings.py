"""
Configurações centrais da aplicação.

Todas as constantes, URLs de API e mapeamentos de UF vivem aqui para
facilitar manutenção e evitar "números/strings mágicos" espalhados pelo código.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# Caminhos base
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
CACHE_DIR = DATA_DIR / "cache"
ASSETS_DIR = BASE_DIR / "assets"
CSS_PATH = ASSETS_DIR / "css" / "style.css"

CACHE_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# APIs do IBGE
# ---------------------------------------------------------------------------
SIDRA_BASE_URL = os.getenv("SIDRA_BASE_URL", "https://apisidra.ibge.gov.br")
LOCALIDADES_BASE_URL = os.getenv(
    "LOCALIDADES_BASE_URL", "https://servicodados.ibge.gov.br/api/v1/localidades"
)
MALHAS_BASE_URL = "https://servicodados.ibge.gov.br/api/v3/malhas"

REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "15"))
USE_LOCAL_CACHE_FALLBACK = os.getenv("USE_LOCAL_CACHE_FALLBACK", "true").lower() == "true"
CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", "21600"))

# Tabela 6407 - Rendimento médio mensal real de todos os trabalhos,
# das pessoas de 14 anos ou mais de idade, ocupadas na semana de referência,
# por Unidade da Federação (PNAD Contínua).
SIDRA_TABLE_RENDIMENTO_UF = "6407"
SIDRA_VAR_RENDIMENTO_MEDIO = "5933"

# Tabela 5436 - Rendimento médio mensal por UF e Grupamento de atividade
# (usada para o Top 3 de setores no hover do mapa).
SIDRA_TABLE_RENDIMENTO_SETOR_UF = "5436"
SIDRA_VAR_RENDIMENTO_SETOR = "5929"
SIDRA_CLASSIFICACAO_SETOR = "11913"  # Grupamento de atividade no trabalho principal

# ---------------------------------------------------------------------------
# Mapeamento de UFs (sigla <-> nome <-> código IBGE)
# ---------------------------------------------------------------------------
UF_INFO: dict[str, dict] = {
    "RO": {"nome": "Rondônia", "codigo_ibge": 11, "regiao": "Norte"},
    "AC": {"nome": "Acre", "codigo_ibge": 12, "regiao": "Norte"},
    "AM": {"nome": "Amazonas", "codigo_ibge": 13, "regiao": "Norte"},
    "RR": {"nome": "Roraima", "codigo_ibge": 14, "regiao": "Norte"},
    "PA": {"nome": "Pará", "codigo_ibge": 15, "regiao": "Norte"},
    "AP": {"nome": "Amapá", "codigo_ibge": 16, "regiao": "Norte"},
    "TO": {"nome": "Tocantins", "codigo_ibge": 17, "regiao": "Norte"},
    "MA": {"nome": "Maranhão", "codigo_ibge": 21, "regiao": "Nordeste"},
    "PI": {"nome": "Piauí", "codigo_ibge": 22, "regiao": "Nordeste"},
    "CE": {"nome": "Ceará", "codigo_ibge": 23, "regiao": "Nordeste"},
    "RN": {"nome": "Rio Grande do Norte", "codigo_ibge": 24, "regiao": "Nordeste"},
    "PB": {"nome": "Paraíba", "codigo_ibge": 25, "regiao": "Nordeste"},
    "PE": {"nome": "Pernambuco", "codigo_ibge": 26, "regiao": "Nordeste"},
    "AL": {"nome": "Alagoas", "codigo_ibge": 27, "regiao": "Nordeste"},
    "SE": {"nome": "Sergipe", "codigo_ibge": 28, "regiao": "Nordeste"},
    "BA": {"nome": "Bahia", "codigo_ibge": 29, "regiao": "Nordeste"},
    "MG": {"nome": "Minas Gerais", "codigo_ibge": 31, "regiao": "Sudeste"},
    "ES": {"nome": "Espírito Santo", "codigo_ibge": 32, "regiao": "Sudeste"},
    "RJ": {"nome": "Rio de Janeiro", "codigo_ibge": 33, "regiao": "Sudeste"},
    "SP": {"nome": "São Paulo", "codigo_ibge": 35, "regiao": "Sudeste"},
    "PR": {"nome": "Paraná", "codigo_ibge": 41, "regiao": "Sul"},
    "SC": {"nome": "Santa Catarina", "codigo_ibge": 42, "regiao": "Sul"},
    "RS": {"nome": "Rio Grande do Sul", "codigo_ibge": 43, "regiao": "Sul"},
    "MS": {"nome": "Mato Grosso do Sul", "codigo_ibge": 50, "regiao": "Centro-Oeste"},
    "MT": {"nome": "Mato Grosso", "codigo_ibge": 51, "regiao": "Centro-Oeste"},
    "GO": {"nome": "Goiás", "codigo_ibge": 52, "regiao": "Centro-Oeste"},
    "DF": {"nome": "Distrito Federal", "codigo_ibge": 53, "regiao": "Centro-Oeste"},
}

CODIGO_TO_UF: dict[int, str] = {v["codigo_ibge"]: k for k, v in UF_INFO.items()}

# ---------------------------------------------------------------------------
# Faixas de cor (iguais à legenda do print de referência)
# ---------------------------------------------------------------------------
FAIXAS_SALARIO = [
    {"min": 2720, "max": 3199.99, "cor": "#DCEBFB", "label": "R$ 2.720 a R$ 3.199"},
    {"min": 3200, "max": 3599.99, "cor": "#A9CFF3", "label": "R$ 3.200 a R$ 3.599"},
    {"min": 3600, "max": 3999.99, "cor": "#5FA3E8", "label": "R$ 3.600 a R$ 3.999"},
    {"min": 4000, "max": 5999.99, "cor": "#1E6FD9", "label": "R$ 4.000 a R$ 5.999"},
    {"min": 6000, "max": 99999, "cor": "#0B3C82", "label": "R$ 6.000 a R$ 6.845"},
]

CUSTOM_COLORSCALE = [
    [0.0, "#DCEBFB"],
    [0.25, "#A9CFF3"],
    [0.5, "#5FA3E8"],
    [0.75, "#1E6FD9"],
    [1.0, "#0B3C82"],
]

APP_TITLE = "Salário Médio da População por Estado no Brasil"
APP_SUBTITLE = "Fonte: PNAD Contínua (IBGE) via API SIDRA"
FONTE_LABEL = "Fonte: PNAD Contínua (IBGE) — dados em tempo real via API SIDRA"

# Opções do filtro de janela histórica (em anos) exibido na aba "Histórico"
ANOS_HISTORICO_OPCOES = [1, 2, 3, 5, 10]
ANOS_HISTORICO_PADRAO = 5


@dataclass(frozen=True)
class Endpoints:
    """Monta as URLs finais consumidas pelo cliente da API."""

    sidra_base: str = SIDRA_BASE_URL
    localidades_base: str = LOCALIDADES_BASE_URL

    def rendimento_uf(self, periodo: str = "last") -> str:
        return (
            f"{self.sidra_base}/values/t/{SIDRA_TABLE_RENDIMENTO_UF}"
            f"/n3/all/v/{SIDRA_VAR_RENDIMENTO_MEDIO}/p/{periodo}/c58/allxt"
        )

    def rendimento_setor_uf(self, periodo: str = "last") -> str:
        return (
            f"{self.sidra_base}/values/t/{SIDRA_TABLE_RENDIMENTO_SETOR_UF}"
            f"/n3/all/v/{SIDRA_VAR_RENDIMENTO_SETOR}/p/{periodo}"
            f"/c{SIDRA_CLASSIFICACAO_SETOR}/all"
        )

    def rendimento_historico_brasil(self, periodo: str = "all") -> str:
        """Série histórica (nível Brasil) do rendimento médio mensal — usada
        na aba de Histórico para calcular variações %MoM/%QoQ e %YoY."""
        return (
            f"{self.sidra_base}/values/t/{SIDRA_TABLE_RENDIMENTO_UF}"
            f"/n1/1/v/{SIDRA_VAR_RENDIMENTO_MEDIO}/p/{periodo}/c58/allxt"
        )

    def malha_uf_geojson(self) -> str:
        return f"{MALHAS_BASE_URL}/BR?formato=application/vnd.geo+json&resolucao=2"

    def estados(self) -> str:
        return f"{self.localidades_base}/estados"


ENDPOINTS = Endpoints()
