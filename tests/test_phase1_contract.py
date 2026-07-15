from pathlib import Path
from typing import get_type_hints
from types import SimpleNamespace


def test_env_example_contains_required_variables():
    content = Path(".env.example").read_text(encoding="utf-8")

    required_keys = [
        "LLM_API_KEY",
        "LLM_BASE_URL",
        "LLM_MODEL",
        "LLM_TIMEOUT_SECONDS",
        "LLM_MAX_RETRIES",
        "EMBEDDING_TIMEOUT_SECONDS",
        "EMBEDDING_MAX_RETRIES",
        "YFINANCE_TIMEOUT_SECONDS",
        "LANGSMITH_TRACING",
        "LANGSMITH_ENDPOINT",
        "LANGSMITH_API_KEY",
        "LANGSMITH_PROJECT",
        "MCP_ENABLED",
        "MCP_SERVER_COMMAND",
        "MCP_SERVER_ARGS",
        "MCP_TIMEOUT_SECONDS",
    ]

    for key in required_keys:
        assert f"{key}=" in content

    assert "LANGCHAIN_API_KEY=" not in content
    assert "LANGCHAIN_PROJECT=" not in content


def test_agent_state_declares_shared_graph_fields():
    from sora.state import AgentState

    hints = get_type_hints(AgentState, include_extras=True)

    assert set(hints) >= {
        "messages",
        "ticker",
        "analyst_report",
        "compliance_status",
    }


def test_stock_tool_handles_empty_ticker():
    from sora.tools import get_stock_data

    result = get_stock_data.invoke({"ticker": ""})

    assert result["status"] == "error"
    assert "ticker" in result["message"].lower()


def test_compliance_tool_handles_missing_rag_module():
    from sora.tools import search_compliance_policy

    result = search_compliance_policy.invoke({"query": "guaranteed returns"})

    assert result["status"] in {"ok", "error"}
    assert "rules" in result


def test_stock_tool_passes_timeout_to_yfinance(monkeypatch):
    import sys
    from sora.tools import get_stock_data

    captured = {}

    class FakeClose:
        @property
        def iloc(self):
            return self

        def __getitem__(self, index):
            assert index == -1
            return 123.45

    class FakeHistory:
        empty = False

        def __contains__(self, key):
            return key == "Close"

        def __getitem__(self, key):
            assert key == "Close"
            return FakeClose()

    class FakeTicker:
        fast_info = {
            "last_price": 123.45,
            "previous_close": 120.0,
            "currency": "USD",
            "market_cap": 1000,
        }

        def __init__(self, ticker):
            captured["ticker"] = ticker

        def history(self, **kwargs):
            captured["history_kwargs"] = kwargs
            return FakeHistory()

    monkeypatch.setitem(sys.modules, "yfinance", SimpleNamespace(Ticker=FakeTicker))
    monkeypatch.setenv("YFINANCE_TIMEOUT_SECONDS", "4")

    result = get_stock_data.invoke({"ticker": "AAPL"})

    assert result["status"] == "ok"
    assert captured["ticker"] == "AAPL"
    assert captured["history_kwargs"]["timeout"] == 4.0
