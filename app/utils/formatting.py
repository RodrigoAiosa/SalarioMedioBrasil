"""Funções de formatação usadas na interface (moeda BRL, percentuais, etc.)."""
from __future__ import annotations


def format_brl(value: float | int | None, decimals: int = 2) -> str:
    """Formata um número no padrão monetário brasileiro: R$ 3.932,45."""
    if value is None:
        return "—"
    formatted = f"{value:,.{decimals}f}"
    # troca separadores: 1,234.56 -> 1.234,56
    formatted = formatted.replace(",", "§").replace(".", ",").replace("§", ".")
    return f"R$ {formatted}"


def format_number(value: float | int | None, decimals: int = 0) -> str:
    """Formata um número simples no padrão brasileiro (sem prefixo de moeda)."""
    if value is None:
        return "—"
    formatted = f"{value:,.{decimals}f}"
    formatted = formatted.replace(",", "§").replace(".", ",").replace("§", ".")
    return formatted
