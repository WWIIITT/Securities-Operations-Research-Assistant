from __future__ import annotations

from typing import Any, Callable

from market_symbols import resolve_market_symbol

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
        info = stock.info or {}
        history = stock.history(period="1d")
    except Exception as exc:
        return {
            "status": "error",
            "message": f"Unable to fetch market data for {normalized_ticker}: {exc}",
            "ticker": normalized_ticker,
            "requested_symbol": symbol["query_symbol"],
        }

    if history.empty and not info:
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
        "currency": info.get("currency"),
        "current_price": info.get("currentPrice") or info.get("regularMarketPrice") or latest_close,
        "previous_close": info.get("previousClose"),
        "market_cap": info.get("marketCap"),
        "sector": info.get("sector"),
        "summary": info.get("longBusinessSummary"),
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
        from rag import get_vector_store
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
