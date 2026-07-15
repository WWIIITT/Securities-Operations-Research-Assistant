from __future__ import annotations

from typing import TypedDict


class MarketSymbol(TypedDict):
    query_symbol: str
    yfinance_symbol: str
    label: str


MARKET_SYMBOL_ALIASES: dict[str, MarketSymbol] = {
    "HK50": {
        "query_symbol": "HK50",
        "yfinance_symbol": "^HSI",
        "label": "Hang Seng Index (HK50 / HSI)",
    },
    "HSI": {
        "query_symbol": "HSI",
        "yfinance_symbol": "^HSI",
        "label": "Hang Seng Index",
    },
    "HANGSENG": {
        "query_symbol": "HANGSENG",
        "yfinance_symbol": "^HSI",
        "label": "Hang Seng Index",
    },
    "HANG SENG": {
        "query_symbol": "HANG SENG",
        "yfinance_symbol": "^HSI",
        "label": "Hang Seng Index",
    },
    "US500": {
        "query_symbol": "US500",
        "yfinance_symbol": "^GSPC",
        "label": "S&P 500 Index",
    },
    "SPX": {
        "query_symbol": "SPX",
        "yfinance_symbol": "^GSPC",
        "label": "S&P 500 Index",
    },
    "NAS100": {
        "query_symbol": "NAS100",
        "yfinance_symbol": "^IXIC",
        "label": "Nasdaq Composite Index",
    },
    "NDX": {
        "query_symbol": "NDX",
        "yfinance_symbol": "^NDX",
        "label": "Nasdaq 100 Index",
    },
}


def resolve_market_symbol(symbol: str) -> MarketSymbol:
    """Resolve common market/index aliases to yfinance-compatible symbols."""
    raw_symbol = (symbol or "").strip()
    compact = raw_symbol.upper().replace("_", " ").replace("-", " ")
    compact_no_space = compact.replace(" ", "")
    alias = MARKET_SYMBOL_ALIASES.get(compact) or MARKET_SYMBOL_ALIASES.get(compact_no_space)
    if alias:
        return alias

    return {
        "query_symbol": raw_symbol.upper(),
        "yfinance_symbol": raw_symbol.upper(),
        "label": raw_symbol.upper(),
    }
