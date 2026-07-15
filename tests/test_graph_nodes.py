import nodes


def test_router_node_routes_stock_query_to_market_analysis():
    result = nodes.router_node({"messages": [{"role": "user", "content": "Analyze AAPL stock"}]})

    assert result["route"] == "market_analysis"
    assert "market" in result["compliance_status"].lower()


def test_router_node_routes_policy_query_to_compliance_check():
    result = nodes.router_node(
        {"messages": [{"role": "user", "content": "Can we promise guaranteed returns?"}]}
    )

    assert result["route"] == "compliance_check"
    assert "compliance" in result["compliance_status"].lower()


def test_analyst_node_extracts_ticker_and_writes_report(monkeypatch):
    class FakeStockTool:
        @staticmethod
        def invoke(payload):
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

    monkeypatch.setattr(nodes, "get_stock_data", FakeStockTool())

    result = nodes.analyst_node({"messages": [{"role": "user", "content": "Analyze AAPL stock"}]})

    assert result["ticker"] == "AAPL"
    assert "Apple Inc." in result["analyst_report"]
    assert "210.5" in result["analyst_report"]


def test_reviewer_node_retrieves_rule_and_appends_disclaimer(monkeypatch):
    class FakeComplianceTool:
        @staticmethod
        def invoke(payload):
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

    monkeypatch.setattr(nodes, "search_compliance_policy", FakeComplianceTool())

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
    import graph

    class FakeStockTool:
        @staticmethod
        def invoke(payload):
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

    class FakeComplianceTool:
        @staticmethod
        def invoke(payload):
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

    monkeypatch.setattr(nodes, "get_stock_data", FakeStockTool())
    monkeypatch.setattr(nodes, "search_compliance_policy", FakeComplianceTool())

    app = graph.build_graph()
    result = app.invoke({"messages": [{"role": "user", "content": "Analyze AAPL stock"}]})

    assert result["route"] == "market_analysis"
    assert result["ticker"] == "AAPL"
    assert "Apple Inc." in result["analyst_report"]
    assert "Do not guarantee returns." in result["analyst_report"]
