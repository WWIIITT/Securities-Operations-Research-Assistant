import nodes


class FakeResponse:
    def __init__(self, content):
        self.content = content


class FakeLLM:
    def __init__(self, content):
        self.content = content
        self.calls = []

    def invoke(self, messages):
        self.calls.append(messages)
        return FakeResponse(self.content)


def test_build_chat_model_reads_openai_compatible_env(monkeypatch):
    import llm

    captured = {}

    class FakeChatOpenAI:
        def __init__(self, **kwargs):
            captured.update(kwargs)

    monkeypatch.setenv("LLM_API_KEY", "test-key")
    monkeypatch.setenv("LLM_BASE_URL", "https://api.vectorengine.cn/v1")
    monkeypatch.setenv("LLM_MODEL", "gpt-4o-mini")
    monkeypatch.setattr(llm, "ChatOpenAI", FakeChatOpenAI)

    model = llm.build_chat_model()

    assert isinstance(model, FakeChatOpenAI)
    assert captured["api_key"] == "test-key"
    assert captured["base_url"] == "https://api.vectorengine.cn/v1"
    assert captured["model"] == "gpt-4o-mini"


def test_router_node_uses_llm_when_available(monkeypatch):
    fake_llm = FakeLLM("market_analysis")
    monkeypatch.setattr(nodes, "build_chat_model", lambda: fake_llm)

    result = nodes.router_node({"messages": [{"role": "user", "content": "Should I analyze Apple?"}]})

    assert result["route"] == "market_analysis"
    assert fake_llm.calls


def test_analyst_node_uses_llm_to_write_report(monkeypatch):
    fake_llm = FakeLLM("LLM analyst report for Apple with market context.")
    monkeypatch.setattr(nodes, "build_chat_model", lambda: fake_llm)
    monkeypatch.setattr(
        nodes,
        "call_tool",
        lambda name, payload: {
            "status": "ok",
            "ticker": payload["ticker"],
            "company_name": "Apple Inc.",
            "current_price": 210.5,
            "currency": "USD",
        },
    )

    result = nodes.analyst_node({"messages": [{"role": "user", "content": "Analyze AAPL"}]})

    assert result["ticker"] == "AAPL"
    assert result["analyst_report"] == "LLM analyst report for Apple with market context."
    assert fake_llm.calls


def test_reviewer_node_uses_llm_but_keeps_mandatory_disclosures(monkeypatch):
    fake_llm = FakeLLM("LLM compliance review paragraph.")
    monkeypatch.setattr(nodes, "build_chat_model", lambda: fake_llm)
    monkeypatch.setattr(
        nodes,
        "call_tool",
        lambda name, payload: {
            "status": "ok",
            "rules": [
                {
                    "content": "Do not guarantee returns.",
                    "metadata": {"rule_id": "RULE-001"},
                }
            ],
        },
    )

    result = nodes.reviewer_node({"analyst_report": "Apple market report."})

    final_report = result["analyst_report"]
    assert "LLM compliance review paragraph." in final_report
    assert "Do not guarantee returns." in final_report
    assert "Risk disclosure" in final_report
    assert "not investment advice" in final_report.lower()
    assert fake_llm.calls
