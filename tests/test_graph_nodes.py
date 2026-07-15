import sora.nodes as nodes


def test_router_node_routes_stock_query_to_market_analysis(monkeypatch):
    monkeypatch.setattr(nodes, "build_chat_model", lambda: (_ for _ in ()).throw(RuntimeError("no llm")))

    result = nodes.router_node({"messages": [{"role": "user", "content": "Analyze AAPL stock"}]})

    assert result["route"] == "market_analysis"
    assert "market" in result["compliance_status"].lower()


def test_router_node_routes_policy_query_to_compliance_check(monkeypatch):
    monkeypatch.setattr(nodes, "build_chat_model", lambda: (_ for _ in ()).throw(RuntimeError("no llm")))

    result = nodes.router_node(
        {"messages": [{"role": "user", "content": "Can we promise guaranteed returns?"}]}
    )

    assert result["route"] == "compliance_check"
    assert "compliance" in result["compliance_status"].lower()


def test_analyst_node_extracts_ticker_and_writes_report(monkeypatch):
    monkeypatch.setattr(nodes, "build_chat_model", lambda: (_ for _ in ()).throw(RuntimeError("no llm")))

    def fake_call_tool(name, payload):
        assert name == "get_stock_data"
        assert payload == {"ticker": "AAPL"}
        return {
            "status": "ok",
            "ticker": "AAPL",
            "company_name": "Apple Inc.",
            "currency": "USD",
            "current_price": 210.5,
            "previous_close": 208.0,
            "market_cap": 3200000000000,
            "sector": "Technology",
            "summary": "Consumer electronics and services.",
        }

    monkeypatch.setattr(nodes, "call_tool", fake_call_tool)

    result = nodes.analyst_node({"messages": [{"role": "user", "content": "Analyze AAPL stock"}]})

    assert result["ticker"] == "AAPL"
    assert "Apple Inc." in result["analyst_report"]
    assert "210.5" in result["analyst_report"]


def test_reviewer_node_retrieves_rule_and_appends_disclaimer(monkeypatch):
    monkeypatch.setattr(nodes, "build_chat_model", lambda: (_ for _ in ()).throw(RuntimeError("no llm")))

    def fake_call_tool(name, payload):
        assert name == "search_compliance_policy"
        assert "Apple report" in payload["query"]
        return {
            "status": "ok",
            "message": "Compliance rules retrieved.",
            "rules": [
                {
                    "content": "Always disclose risks.",
                    "metadata": {"rule_id": "RULE-002"},
                }
            ],
        }

    monkeypatch.setattr(nodes, "call_tool", fake_call_tool)

    result = nodes.reviewer_node(
        {
            "analyst_report": "Apple report with market context.",
            "messages": [{"role": "user", "content": "Analyze AAPL stock"}],
        }
    )

    assert result["compliance_status"] == "approved_with_disclosures"
    assert "Always disclose risks." in result["analyst_report"]
    assert "Risk disclosure" in result["analyst_report"]
    assert "not investment advice" in result["analyst_report"].lower()


def test_build_graph_invokes_analyst_then_reviewer(monkeypatch):
    import sora.graph as graph
    monkeypatch.setattr(nodes, "build_chat_model", lambda: (_ for _ in ()).throw(RuntimeError("no llm")))

    def fake_call_tool(name, payload):
        if name == "get_stock_data":
            return {
                "status": "ok",
                "ticker": payload["ticker"],
                "company_name": "Apple Inc.",
                "currency": "USD",
                "current_price": 210.5,
                "previous_close": 208.0,
                "market_cap": 3200000000000,
                "sector": "Technology",
                "summary": "Consumer electronics and services.",
            }
        return {
            "status": "ok",
            "message": "Compliance rules retrieved.",
            "rules": [
                {
                    "content": "Do not guarantee returns.",
                    "metadata": {"rule_id": "RULE-001"},
                }
            ],
        }

    monkeypatch.setattr(nodes, "call_tool", fake_call_tool)

    app = graph.build_graph()
    result = app.invoke({"messages": [{"role": "user", "content": "Analyze AAPL stock"}]})

    assert result["route"] == "market_analysis"
    assert result["ticker"] == "AAPL"
    assert "Apple Inc." in result["analyst_report"]
    assert "Do not guarantee returns." in result["analyst_report"]


def test_analyst_node_uses_external_crypto_mcp_tool_for_bitcoin(monkeypatch):
    monkeypatch.setattr(nodes, "build_chat_model", lambda: (_ for _ in ()).throw(RuntimeError("no llm")))

    calls = []

    def fake_call_tool(name, payload):
        calls.append((name, payload))
        if name == "get_crypto_price":
            return {
                "status": "ok",
                "asset": "BTC",
                "asset_id": "bitcoin",
                "vs_currency": "usd",
                "current_price": 65000.5,
                "market_cap": 1200000000000,
                "price_change_percentage_24h": 2.5,
                "source": "coingecko",
            }
        return {"status": "ok", "rules": []}

    monkeypatch.setattr(nodes, "call_tool", fake_call_tool)

    result = nodes.analyst_node({"messages": [{"role": "user", "content": "What is Bitcoin price now?"}]})

    assert calls == [("get_crypto_price", {"asset": "bitcoin", "vs_currency": "usd"})]
    assert result["ticker"] == "BTC"
    assert "65000.5" in result["analyst_report"]
