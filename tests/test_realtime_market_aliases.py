import sora.nodes as nodes
from sora.market_symbols import resolve_market_symbol


def test_hk50_alias_resolves_to_hang_seng_yfinance_symbol():
    resolved = resolve_market_symbol("HK50")

    assert resolved["query_symbol"] == "HK50"
    assert resolved["yfinance_symbol"] == "^HSI"
    assert "Hang Seng" in resolved["label"]


def test_extract_ticker_handles_hk50_index_alias():
    assert nodes.extract_ticker("what is the price of HK50 now") == "^HSI"


def test_analyst_node_uses_tool_data_when_llm_claims_no_realtime_access(monkeypatch):
    class FakeLLM:
        @staticmethod
        def invoke(messages):
            class Response:
                content = "As of my last update, I do not have real-time data access."

            return Response()

    def fake_call_tool(name, payload):
        assert name == "get_stock_data"
        assert payload == {"ticker": "^HSI"}
        return {
            "status": "ok",
            "ticker": "^HSI",
            "requested_symbol": "HK50",
            "company_name": "Hang Seng Index",
            "currency": "HKD",
            "current_price": 18250.12,
            "previous_close": 18100.0,
            "market_cap": None,
            "sector": "Index",
            "summary": "Hong Kong equity benchmark index.",
        }

    monkeypatch.setattr(nodes, "build_chat_model", lambda: FakeLLM())
    monkeypatch.setattr(nodes, "call_tool", fake_call_tool)

    result = nodes.analyst_node({"messages": [{"role": "user", "content": "what is the price of HK50 now"}]})

    assert result["ticker"] == "^HSI"
    assert "18250.12" in result["analyst_report"]
    assert "I do not have real-time data access" not in result["analyst_report"]
