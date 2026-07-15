from __future__ import annotations

import json
import statistics
import time
from pathlib import Path
from typing import Any, Callable

from tools import search_compliance_policy

RAG_EVAL_CASES = [
    {
        "query": "Can we guarantee returns to clients?",
        "expected_rule_ids": ["RULE-001"],
    },
    {
        "query": "What risk disclosure is required in market commentary?",
        "expected_rule_ids": ["RULE-002"],
    },
    {
        "query": "Is this output investment advice?",
        "expected_rule_ids": ["RULE-003"],
    },
    {
        "query": "Should we mention limitations and data uncertainty?",
        "expected_rule_ids": ["RULE-004"],
    },
]


def _percentile(values: list[float], percentile: float) -> float:
    if not values:
        return 0.0
    if len(values) == 1:
        return round(values[0], 2)

    sorted_values = sorted(values)
    index = (len(sorted_values) - 1) * percentile
    lower = int(index)
    upper = min(lower + 1, len(sorted_values) - 1)
    weight = index - lower
    return round(sorted_values[lower] * (1 - weight) + sorted_values[upper] * weight, 2)


def calculate_metrics(results: list[dict[str, Any]]) -> dict[str, Any]:
    """Calculate retrieval quality and latency metrics for RAG evaluation."""
    total = len(results)
    if total == 0:
        return {
            "total_queries": 0,
            "hit_at_1": 0.0,
            "hit_at_3": 0.0,
            "mrr": 0.0,
            "avg_latency_ms": 0.0,
            "p95_latency_ms": 0.0,
        }

    hit_at_1 = 0
    hit_at_3 = 0
    reciprocal_ranks: list[float] = []
    latencies = [float(result.get("latency_ms", 0.0)) for result in results]

    for result in results:
        expected = set(result.get("expected_rule_ids", []))
        retrieved = result.get("retrieved_rule_ids", [])
        first_three = retrieved[:3]

        if retrieved[:1] and expected.intersection(retrieved[:1]):
            hit_at_1 += 1
        if expected.intersection(first_three):
            hit_at_3 += 1

        rank = next(
            (index for index, rule_id in enumerate(retrieved, start=1) if rule_id in expected),
            None,
        )
        reciprocal_ranks.append(0.0 if rank is None else 1.0 / rank)

    return {
        "total_queries": total,
        "hit_at_1": round(hit_at_1 / total, 4),
        "hit_at_3": round(hit_at_3 / total, 4),
        "mrr": round(sum(reciprocal_ranks) / total, 4),
        "avg_latency_ms": round(statistics.fmean(latencies), 2),
        "p95_latency_ms": _percentile(latencies, 0.95),
    }


def evaluate_rag(
    search_fn: Callable[[dict[str, str]], dict[str, Any]] | None = None,
    cases: list[dict[str, Any]] | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Run the compliance RAG retrieval test set and return results plus metrics."""
    search = search_fn or search_compliance_policy.invoke
    eval_cases = cases or RAG_EVAL_CASES
    results: list[dict[str, Any]] = []

    for case in eval_cases:
        started = time.perf_counter()
        response = search({"query": case["query"]})
        latency_ms = (time.perf_counter() - started) * 1000
        rules = response.get("rules", [])
        retrieved_rule_ids = [
            rule.get("metadata", {}).get("rule_id", "")
            for rule in rules
            if rule.get("metadata", {}).get("rule_id")
        ]
        results.append(
            {
                "query": case["query"],
                "expected_rule_ids": case["expected_rule_ids"],
                "retrieved_rule_ids": retrieved_rule_ids,
                "latency_ms": round(latency_ms, 2),
                "status": response.get("status", "unknown"),
                "message": response.get("message", ""),
            }
        )

    return results, calculate_metrics(results)


def write_report(
    output_path: str | Path = "rag_eval_report.json",
    results: list[dict[str, Any]] | None = None,
    metrics: dict[str, Any] | None = None,
) -> Path:
    """Write a RAG evaluation report as JSON."""
    path = Path(output_path)
    payload = {
        "metrics": metrics or {},
        "results": results or [],
    }
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def main() -> None:
    results, metrics = evaluate_rag()
    output_path = write_report(results=results, metrics=metrics)
    print(f"RAG evaluation report written to {output_path}")
    print(json.dumps(metrics, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
