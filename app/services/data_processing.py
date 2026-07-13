"""
Transforma as respostas brutas da API SIDRA (lista de dicts, com cabeçalho
na primeira posição) em estruturas prontas para uso na interface:

  - DataFrame de rendimento médio por UF (com sigla, cor da faixa, etc.)
  - Dicionário {sigla_uf: [(setor, valor), (setor, valor), (setor, valor)]}
    com o Top 3 de setores de maior rendimento médio por estado.
"""
from __future__ import annotations

import logging

import pandas as pd

from app.config.settings import CODIGO_TO_UF, FAIXAS_SALARIO, UF_INFO

logger = logging.getLogger(__name__)


def _strip_sidra_header(raw: list[dict]) -> list[dict]:
    """A API SIDRA retorna o cabeçalho como primeiro elemento da lista; remove-o."""
    if not raw:
        return []
    return raw[1:] if _looks_like_header(raw[0]) else raw


def _looks_like_header(row: dict) -> bool:
    return row.get("D1C") in (None, "Unidade da Federação (Código)")


def _safe_float(value: str | float | None) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def faixa_cor_para_valor(valor: float) -> str:
    """Retorna a cor hexadecimal correspondente à faixa salarial do valor."""
    for faixa in FAIXAS_SALARIO:
        if faixa["min"] <= valor <= faixa["max"]:
            return faixa["cor"]
    return FAIXAS_SALARIO[-1]["cor"]


def faixa_label_para_valor(valor: float) -> str:
    for faixa in FAIXAS_SALARIO:
        if faixa["min"] <= valor <= faixa["max"]:
            return faixa["label"]
    return FAIXAS_SALARIO[-1]["label"]


def build_rendimento_uf_dataframe(raw_rendimento_uf: list[dict]) -> pd.DataFrame:
    """
    Constrói o DataFrame principal: uma linha por UF, com:
      sigla, nome, regiao, rendimento_medio, faixa_cor, faixa_label
    """
    rows = _strip_sidra_header(raw_rendimento_uf)

    records = []
    for row in rows:
        codigo = int(row["D1C"])
        sigla = CODIGO_TO_UF.get(codigo)
        if sigla is None:
            continue
        valor = _safe_float(row.get("V"))
        if valor is None:
            continue
        info = UF_INFO[sigla]
        records.append(
            {
                "sigla": sigla,
                "nome": info["nome"],
                "regiao": info["regiao"],
                "codigo_ibge": codigo,
                "rendimento_medio": valor,
                "faixa_cor": faixa_cor_para_valor(valor),
                "faixa_label": faixa_label_para_valor(valor),
            }
        )

    df = pd.DataFrame.from_records(records)
    if df.empty:
        logger.warning("DataFrame de rendimento por UF veio vazio.")
        return df

    return df.sort_values("rendimento_medio", ascending=False).reset_index(drop=True)


def build_top_setores_por_uf(raw_rendimento_setor_uf: list[dict], top_n: int = 3) -> dict[str, list[dict]]:
    """
    Constrói um dicionário:
        {"SP": [{"setor": "...", "valor": 8000.0}, ...top_n], "RJ": [...], ...}

    ordenado do maior para o menor rendimento médio setorial dentro de cada UF.
    """
    rows = _strip_sidra_header(raw_rendimento_setor_uf)

    df = pd.DataFrame(rows)
    if df.empty:
        return {}

    df["codigo_ibge"] = df["D1C"].astype(int)
    df["sigla"] = df["codigo_ibge"].map(CODIGO_TO_UF)
    df["valor"] = df["V"].apply(_safe_float)
    df["setor"] = df["D4N"]

    df = df.dropna(subset=["sigla", "valor"])

    result: dict[str, list[dict]] = {}
    for sigla, group in df.groupby("sigla"):
        top = group.sort_values("valor", ascending=False).head(top_n)
        result[sigla] = [
            {"setor": _shorten_setor_label(r.setor), "valor": r.valor}
            for r in top.itertuples(index=False)
        ]
    return result


def _shorten_setor_label(label: str, max_len: int = 42) -> str:
    """Encurta nomes longos de grupamento de atividade para caber no tooltip."""
    if len(label) <= max_len:
        return label
    truncated = label[: max_len - 1].rsplit(" ", 1)[0].rstrip(",")
    return truncated + "…"


def build_hover_text(df: pd.DataFrame, top_setores: dict[str, list[dict]]) -> pd.Series:
    """
    Monta o texto de hover (multi-linha) combinando rendimento médio da UF
    com o Top 3 de setores daquela UF.
    """
    from app.utils.formatting import format_brl

    def _row_hover(row: pd.Series) -> str:
        linhas = [
            f"<b>{row['nome']} ({row['sigla']})</b>",
            f"Rendimento médio: <b>{format_brl(row['rendimento_medio'])}</b>",
            "",
            "<b>Top 3 setores (maior média salarial):</b>",
        ]
        setores = top_setores.get(row["sigla"], [])
        if not setores:
            linhas.append("Sem dados setoriais disponíveis")
        else:
            for i, item in enumerate(setores, start=1):
                linhas.append(f"{i}. {item['setor']} — {format_brl(item['valor'])}")
        return "<br>".join(linhas)

    return df.apply(_row_hover, axis=1)


def compute_summary_metrics(df: pd.DataFrame) -> dict:
    """Calcula métricas resumo: média Brasil, maior UF, menor UF."""
    if df.empty:
        return {"media_brasil": None, "maior_uf": None, "menor_uf": None}

    media_brasil = df["rendimento_medio"].mean()
    maior = df.iloc[df["rendimento_medio"].idxmax()]
    menor = df.iloc[df["rendimento_medio"].idxmin()]

    return {
        "media_brasil": media_brasil,
        "maior_uf": {"sigla": maior["sigla"], "nome": maior["nome"], "valor": maior["rendimento_medio"]},
        "menor_uf": {"sigla": menor["sigla"], "nome": menor["nome"], "valor": menor["rendimento_medio"]},
    }


_MESES_PT = {
    1: "Jan", 2: "Fev", 3: "Mar", 4: "Abr", 5: "Mai", 6: "Jun",
    7: "Jul", 8: "Ago", 9: "Set", 10: "Out", 11: "Nov", 12: "Dez",
}
# Mapeia o trimestre da PNAD Contínua para o mês final do trimestre (MesAno),
# já que a pesquisa é trimestral, e não mensal.
_TRIMESTRE_PARA_MES = {1: 3, 2: 6, 3: 9, 4: 12}


def build_historico_dataframe(raw_historico: list[dict]) -> pd.DataFrame:
    """
    Constrói o DataFrame da série histórica nacional (nível Brasil) a partir
    da resposta bruta da API SIDRA (Tabela 6407, N1), com colunas:

        ano, trimestre, periodo_label ("Mar/2015"), data_ref (Timestamp),
        rendimento_medio, var_mom (%QoQ), var_yoy (%)

    A PNAD Contínua de rendimento é divulgada trimestralmente (não mensal);
    por isso a variação "MoM" é calculada entre trimestres consecutivos
    (equivalente a %QoQ) e rotulada como "Período (MesAno)" usando o último
    mês de cada trimestre, para ficar no formato solicitado (ex.: "Mar/2024").
    """
    rows = _strip_sidra_header(raw_historico)

    records = []
    for row in rows:
        codigo = str(row.get("D3C", ""))
        if len(codigo) != 6:
            continue
        ano = int(codigo[:4])
        trimestre = int(codigo[4:6])
        valor = _safe_float(row.get("V"))
        if valor is None or trimestre not in _TRIMESTRE_PARA_MES:
            continue
        mes = _TRIMESTRE_PARA_MES[trimestre]
        records.append(
            {
                "ano": ano,
                "trimestre": trimestre,
                "mes": mes,
                "data_ref": pd.Timestamp(year=ano, month=mes, day=1),
                "rendimento_medio": valor,
            }
        )

    df = pd.DataFrame.from_records(records)
    if df.empty:
        return df

    df = df.sort_values("data_ref").reset_index(drop=True)
    df["periodo_label"] = df.apply(lambda r: f"{_MESES_PT[r['mes']]}/{r['ano']}", axis=1)
    df["var_mom"] = df["rendimento_medio"].pct_change(1) * 100
    df["var_yoy"] = df["rendimento_medio"].pct_change(4) * 100

    return df


def filter_ultimos_anos(df_historico: pd.DataFrame, anos: int) -> pd.DataFrame:
    """Filtra o DataFrame histórico para os últimos `anos` anos (a partir do período mais recente)."""
    if df_historico.empty:
        return df_historico
    data_limite = df_historico["data_ref"].max() - pd.DateOffset(years=anos)
    return df_historico[df_historico["data_ref"] > data_limite].reset_index(drop=True)
