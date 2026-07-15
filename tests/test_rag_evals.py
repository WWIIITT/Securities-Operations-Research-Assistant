def test_rag_eval_metrics_calculate_hit_rates_and_latency():
    import rag_evals

    results = [
        {
            "expected_rule_ids": ["RULE-001"],
            "retrieved_rule_ids": ["RULE-001", "RULE-002"],
            "latency_ms": 10.0,
        },
        {
            "expected_rule_ids": ["RULE-003"],
            "retrieved_rule_ids": ["RULE-002", "RULE-003"],
            "latency_ms": 30.0,
        },
    ]

    metrics = rag_evals.calculate_metrics(results)

    assert metrics["total_queries"] == 2
    assert metrics["hit_at_1"] == 0.5
    assert metrics["hit_at_3"] == 1.0
    assert metrics["mrr"] == 0.75
    assert metrics["avg_latency_ms"] == 20.0
    assert metrics["p95_latency_ms"] >= 10.0


def test_rag_eval_cases_have_expected_rule_ids():
    import rag_evals

    assert rag_evals.RAG_EVAL_CASES
    assert all(case["query"] for case in rag_evals.RAG_EVAL_CASES)
    assert all(case["expected_rule_ids"] for case in rag_evals.RAG_EVAL_CASES)


def test_rag_eval_report_writer_creates_json(tmp_path):
    import json
    import rag_evals

    output_path = tmp_path / "rag_eval_report.json"
    rag_evals.write_report(
        output_path,
        results=[{"query": "q", "retrieved_rule_ids": ["RULE-001"]}],
        metrics={"hit_at_3": 1.0},
    )

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["metrics"]["hit_at_3"] == 1.0
    assert payload["results"][0]["retrieved_rule_ids"] == ["RULE-001"]
