from pathlib import Path


def test_run_sora_query_returns_report_and_trace_metadata():
    import app

    class FakeGraph:
        @staticmethod
        def invoke(state):
            assert state["messages"][0]["content"] == "Analyze AAPL stock"
            return {
                "analyst_report": "Final compliant report.",
                "route": "market_analysis",
                "ticker": "AAPL",
                "compliance_status": "approved_with_disclosures",
            }

    report, metadata = app.run_sora_query("Analyze AAPL stock", graph_app=FakeGraph())

    assert report == "Final compliant report."
    assert metadata["route"] == "market_analysis"
    assert metadata["ticker"] == "AAPL"
    assert metadata["compliance_status"] == "approved_with_disclosures"


def test_run_sora_query_handles_empty_input_without_invoking_graph():
    import app

    class ExplodingGraph:
        @staticmethod
        def invoke(state):
            raise AssertionError("Graph should not be invoked for empty input.")

    report, metadata = app.run_sora_query("   ", graph_app=ExplodingGraph())

    assert "Enter a financial or compliance question" in report
    assert metadata["status"] == "input_required"


def test_requirements_include_runtime_dependencies():
    requirements = Path("requirements.txt").read_text(encoding="utf-8")

    for package in [
        "langgraph",
        "langchain",
        "langchain-openai",
        "langchain-chroma",
        "chromadb",
        "yfinance",
        "gradio",
        "langsmith",
        "python-dotenv",
    ]:
        assert package in requirements


def test_readme_documents_install_and_run_commands():
    readme = Path("README.md").read_text(encoding="utf-8")

    assert "pip install -r requirements.txt" in readme
    assert "python app.py" in readme
    assert "python evals.py" in readme
    assert "python rag_evals.py" in readme
    assert "python mcp_server.py" in readme
    assert "LANGSMITH_PROJECT" in readme
    assert "LANGCHAIN_API_KEY" not in readme
