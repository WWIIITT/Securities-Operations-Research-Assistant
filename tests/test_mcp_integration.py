def test_mcp_server_registers_expected_tool_names():
    import sora.mcp_server as mcp_server

    assert set(mcp_server.TOOL_NAMES) == {
        "get_stock_data",
        "get_crypto_price",
        "search_compliance_policy",
    }


def test_mcp_client_falls_back_to_local_tools(monkeypatch):
    import sora.mcp_client as mcp_client

    monkeypatch.setenv("MCP_ENABLED", "false")
    result = mcp_client.call_tool("get_stock_data", {"ticker": ""})

    assert result["status"] == "error"
    assert "ticker" in result["message"].lower()


def test_mcp_client_can_call_external_crypto_tool_locally(monkeypatch):
    import sora.mcp_client as mcp_client

    monkeypatch.setenv("MCP_ENABLED", "false")
    monkeypatch.setattr(
        mcp_client,
        "get_crypto_price",
        lambda asset, vs_currency="usd": {
            "status": "ok",
            "asset": asset,
            "vs_currency": vs_currency,
            "current_price": 65000,
        },
    )
    monkeypatch.setitem(mcp_client.LOCAL_TOOLS, "get_crypto_price", mcp_client.get_crypto_price)

    result = mcp_client.call_tool("get_crypto_price", {"asset": "bitcoin"})

    assert result["status"] == "ok"
    assert result["asset"] == "bitcoin"


def test_mcp_client_can_be_monkeypatched_for_nodes(monkeypatch):
    import sora.nodes as nodes

    calls = []

    def fake_call_tool(name, payload):
        calls.append((name, payload))
        if name == "get_stock_data":
            return {"status": "error", "message": "No data", "ticker": payload["ticker"]}
        return {"status": "ok", "rules": []}

    monkeypatch.setattr(nodes, "call_tool", fake_call_tool)
    nodes.analyst_node({"messages": [{"role": "user", "content": "Analyze MSFT"}]})

    assert calls == [("get_stock_data", {"ticker": "MSFT"})]
