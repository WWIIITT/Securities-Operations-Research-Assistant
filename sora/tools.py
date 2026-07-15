from __future__ import annotations

import json
import os
import urllib.parse
import urllib.request
from typing import Any, Callable

from .market_symbols import resolve_market_symbol

CRYPTO_ASSET_ALIASES = {
    "btc": {"asset_id": "bitcoin", "symbol": "BTC", "label": "Bitcoin"},
    "bitcoin": {"asset_id": "bitcoin", "symbol": "BTC", "label": "Bitcoin"},
    "eth": {"asset_id": "ethereum", "symbol": "ETH", "label": "Ethereum"},
    "ethereum": {"asset_id": "ethereum", "symbol": "ETH", "label": "Ethereum"},
    "sol": {"asset_id": "solana", "symbol": "SOL", "label": "Solana"},
    "solana": {"asset_id": "solana", "symbol": "SOL", "label": "Solana"},
}

try:
    from langchain_core.tools import tool
except ImportError:  # Minimal local fallback for tests before dependencies are installed.
    class _FallbackTool:
        def __init__(self, fn: Callable[..., dict[str, Any]]):
            self.fn = fn
            self.name = fn.__name__
            self.description = fn.__doc__ or ""

        def invoke(self, args: dict[str, Any] | str) -> dict[str, Any]:
            if isinstance(args, dict):
                return self.fn(**args)
            return self.fn(args)

        def __call__(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
            return self.fn(*args, **kwargs)

    def tool(fn: Callable[..., dict[str, Any]]) -> _FallbackTool:
        return _FallbackTool(fn)


def _env_float(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, str(default)))
    except ValueError:
        return default


def _env_enabled(name: str, default: bool = False) -> bool:
    fallback = "true" if default else "false"
    return os.getenv(name, fallback).strip().lower() in {"1", "true", "yes", "on"}


def _mapping_get(mapping: Any, *keys: str) -> Any:
    if not mapping:
        return None
    for key in keys:
        try:
            if hasattr(mapping, "get"):
                value = mapping.get(key)
            else:
                value = mapping[key]
        except Exception:
            continue
        if value is not None:
            return value
    return None


def resolve_crypto_asset(asset: str) -> dict[str, str]:
    """Resolve common crypto aliases to CoinGecko asset ids."""
    normalized = (asset or "").strip().lower()
    if not normalized:
        return {"query_asset": "", "asset_id": "", "symbol": "", "label": ""}
    return CRYPTO_ASSET_ALIASES.get(
        normalized,
        {
            "query_asset": asset.strip(),
            "asset_id": normalized,
            "symbol": normalized.upper(),
            "label": asset.strip(),
        },
    ) | {"query_asset": asset.strip()}


@tool
def get_stock_data(ticker: str) -> dict[str, Any]:
    """Fetch current stock data and basic company information from yfinance."""
    symbol = resolve_market_symbol(ticker)
    normalized_ticker = symbol["yfinance_symbol"]
    if not symbol["query_symbol"]:
        return {
            "status": "error",
            "message": "A non-empty ticker is required.",
            "ticker": "",
        }

    try:
        import yfinance as yf
    except ImportError:
        return {
            "status": "error",
            "message": "The yfinance package is not installed. Run the project setup first.",
            "ticker": normalized_ticker,
            "requested_symbol": symbol["query_symbol"],
        }

    try:
        stock = yf.Ticker(normalized_ticker)
        timeout = _env_float("YFINANCE_TIMEOUT_SECONDS", 8.0)
        history = stock.history(period="1d", timeout=timeout)
        try:
            fast_info = stock.fast_info or {}
        except Exception:
            fast_info = {}
        info = {}
        if _env_enabled("YFINANCE_ENABLE_FULL_INFO", False):
            try:
                if hasattr(stock, "get_info"):
                    info = stock.get_info() or {}
                else:
                    info = stock.info or {}
            except Exception:
                info = {}
    except Exception as exc:
        return {
            "status": "error",
            "message": f"Unable to fetch market data for {normalized_ticker}: {exc}",
            "ticker": normalized_ticker,
            "requested_symbol": symbol["query_symbol"],
        }

    if history.empty and not info and not fast_info:
        return {
            "status": "error",
            "message": f"No market data found for ticker {normalized_ticker}.",
            "ticker": normalized_ticker,
            "requested_symbol": symbol["query_symbol"],
        }

    latest_close = None
    if not history.empty and "Close" in history:
        latest_close = float(history["Close"].iloc[-1])

    return {
        "status": "ok",
        "ticker": normalized_ticker,
        "requested_symbol": symbol["query_symbol"],
        "company_name": info.get("shortName") or info.get("longName") or symbol["label"] or normalized_ticker,
        "currency": info.get("currency") or _mapping_get(fast_info, "currency"),
        "current_price": (
            info.get("currentPrice")
            or info.get("regularMarketPrice")
            or _mapping_get(fast_info, "last_price", "regular_market_price")
            or latest_close
        ),
        "previous_close": info.get("previousClose") or _mapping_get(fast_info, "previous_close"),
        "market_cap": info.get("marketCap") or _mapping_get(fast_info, "market_cap"),
        "sector": info.get("sector"),
        "summary": info.get("longBusinessSummary"),
    }


@tool
def get_crypto_price(asset: str, vs_currency: str = "usd") -> dict[str, Any]:
    """Fetch external cryptocurrency price data from the public CoinGecko API."""
    resolved = resolve_crypto_asset(asset)
    if not resolved["asset_id"]:
        return {
            "status": "error",
            "message": "A non-empty crypto asset is required.",
            "asset": "",
        }

    currency = (vs_currency or "usd").strip().lower()
    timeout = _env_float("EXTERNAL_API_TIMEOUT_SECONDS", 8.0)
    query = urllib.parse.urlencode(
        {
            "ids": resolved["asset_id"],
            "vs_currencies": currency,
            "include_market_cap": "true",
            "include_24hr_change": "true",
            "include_last_updated_at": "true",
        }
    )
    url = f"https://api.coingecko.com/api/v3/simple/price?{query}"
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": "SORA-MCP/0.1",
        },
    )

    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except Exception as exc:
        return {
            "status": "error",
            "message": f"Unable to fetch external crypto price for {resolved['asset_id']}: {exc}",
            "asset": resolved["query_asset"],
            "asset_id": resolved["asset_id"],
            "source": "coingecko",
        }

    asset_payload = payload.get(resolved["asset_id"], {})
    price = asset_payload.get(currency)
    if price is None:
        return {
            "status": "error",
            "message": f"No {currency.upper()} price returned for {resolved['asset_id']}.",
            "asset": resolved["query_asset"],
            "asset_id": resolved["asset_id"],
            "source": "coingecko",
        }

    return {
        "status": "ok",
        "asset": resolved["query_asset"],
        "asset_id": resolved["asset_id"],
        "symbol": resolved["symbol"],
        "label": resolved["label"],
        "vs_currency": currency,
        "current_price": price,
        "market_cap": asset_payload.get(f"{currency}_market_cap"),
        "price_change_percentage_24h": asset_payload.get(f"{currency}_24h_change"),
        "last_updated_at": asset_payload.get("last_updated_at"),
        "source": "coingecko",
    }


@tool
def search_compliance_policy(query: str) -> dict[str, Any]:
    """Search the local Chroma compliance policy store for relevant rules."""
    normalized_query = (query or "").strip()
    if not normalized_query:
        return {
            "status": "error",
            "message": "A non-empty compliance query is required.",
            "rules": [],
        }

    try:
        from .rag import get_vector_store
    except ImportError:
        return {
            "status": "error",
            "message": "The RAG module is not available yet. Create rag.py before running compliance search.",
            "rules": [],
        }

    try:
        vector_store = get_vector_store()
        documents = vector_store.similarity_search(normalized_query, k=3)
    except Exception as exc:
        return {
            "status": "error",
            "message": f"Unable to search compliance policy store: {exc}",
            "rules": [],
        }

    rules = [
        {
            "content": document.page_content,
            "metadata": document.metadata,
        }
        for document in documents
    ]

    return {
        "status": "ok" if rules else "error",
        "message": "Compliance rules retrieved." if rules else "No compliance rules matched the query.",
        "rules": rules,
    }
