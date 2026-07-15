from pathlib import Path
from typing import get_type_hints


def test_env_example_contains_required_variables():
    content = Path(".env.example").read_text(encoding="utf-8")

    required_keys = [
        "LLM_API_KEY",
        "LLM_BASE_URL",
        "LLM_MODEL",
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
    from state import AgentState

    hints = get_type_hints(AgentState, include_extras=True)

    assert set(hints) >= {
        "messages",
        "ticker",
        "analyst_report",
        "compliance_status",
    }


def test_stock_tool_handles_empty_ticker():
    from tools import get_stock_data

    result = get_stock_data.invoke({"ticker": ""})

    assert result["status"] == "error"
    assert "ticker" in result["message"].lower()


def test_compliance_tool_handles_missing_rag_module():
    from tools import search_compliance_policy

    result = search_compliance_policy.invoke({"query": "guaranteed returns"})

    assert result["status"] in {"ok", "error"}
    assert "rules" in result
