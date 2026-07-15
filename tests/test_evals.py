import pytest


def test_evaluation_examples_define_inputs_and_expected_topics():
    import evals

    assert len(evals.EVALUATION_EXAMPLES) >= 2
    for example in evals.EVALUATION_EXAMPLES:
        assert example["inputs"]["query"]
        assert example["reference_outputs"]["required_topics"]


def test_sora_target_returns_final_response_from_graph():
    import evals

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

    result = evals.sora_target({"query": "Analyze AAPL stock"}, app=FakeGraph())

    assert result["final_response"] == "Final compliant report."
    assert result["route"] == "market_analysis"
    assert result["ticker"] == "AAPL"


def test_compliance_disclaimer_evaluator_scores_required_topics():
    import evals

    result = evals.compliance_disclaimer_evaluator(
        outputs={
            "final_response": (
                "Risk disclosure: returns are not guaranteed. "
                "This is not investment advice."
            )
        },
        reference_outputs={
            "required_topics": ["risk disclosure", "not guaranteed", "not investment advice"]
        },
    )

    assert result["key"] == "compliance_disclaimers"
    assert result["score"] == 1


def test_compliance_disclaimer_evaluator_reports_missing_topics():
    import evals

    result = evals.compliance_disclaimer_evaluator(
        outputs={"final_response": "Market report only."},
        reference_outputs={"required_topics": ["risk disclosure", "not investment advice"]},
    )

    assert result["score"] == 0
    assert "risk disclosure" in result["comment"]


def test_validate_langsmith_environment_raises_clear_error_without_key(monkeypatch):
    import evals

    monkeypatch.delenv("LANGSMITH_API_KEY", raising=False)

    with pytest.raises(RuntimeError, match="LANGSMITH_API_KEY"):
        evals.validate_langsmith_environment()
