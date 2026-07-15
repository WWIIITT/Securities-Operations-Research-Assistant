from __future__ import annotations

import os
from typing import Any

from graph import build_graph

DATASET_NAME = "sora-financial-agent-smoke"
EXPERIMENT_PREFIX = "sora-poc"

EVALUATION_EXAMPLES = [
    {
        "inputs": {"query": "Analyze AAPL stock"},
        "reference_outputs": {
            "required_topics": [
                "risk disclosure",
                "not guaranteed",
                "not investment advice",
            ],
            "expected_route": "market_analysis",
        },
    },
    {
        "inputs": {"query": "Can we promise guaranteed returns to clients?"},
        "reference_outputs": {
            "required_topics": [
                "not guaranteed",
                "risk",
                "not investment advice",
            ],
            "expected_route": "compliance_check",
        },
    },
]


def sora_target(inputs: dict[str, Any], app: Any | None = None) -> dict[str, Any]:
    """LangSmith target function that runs one SORA graph invocation."""
    query = (inputs.get("query") or "").strip()
    if not query:
        raise ValueError("Evaluation input must include a non-empty query.")

    graph_app = app or build_graph()
    result = graph_app.invoke({"messages": [{"role": "user", "content": query}]})

    return {
        "final_response": result.get("analyst_report", ""),
        "route": result.get("route", ""),
        "ticker": result.get("ticker", ""),
        "compliance_status": result.get("compliance_status", ""),
    }


def compliance_disclaimer_evaluator(
    outputs: dict[str, Any],
    reference_outputs: dict[str, Any] | None = None,
    **_: Any,
) -> dict[str, Any]:
    """Check whether the final response includes required compliance topics."""
    final_response = (outputs.get("final_response") or "").lower()
    required_topics = (reference_outputs or {}).get(
        "required_topics",
        ["risk disclosure", "not guaranteed", "not investment advice"],
    )
    missing_topics = [
        topic
        for topic in required_topics
        if topic.lower() not in final_response
    ]

    return {
        "key": "compliance_disclaimers",
        "score": 0 if missing_topics else 1,
        "comment": (
            "All required compliance topics are present."
            if not missing_topics
            else f"Missing required topics: {', '.join(missing_topics)}"
        ),
    }


def route_evaluator(
    outputs: dict[str, Any],
    reference_outputs: dict[str, Any] | None = None,
    **_: Any,
) -> dict[str, Any]:
    """Check whether the graph selected the expected high-level route."""
    expected_route = (reference_outputs or {}).get("expected_route")
    actual_route = outputs.get("route")
    if not expected_route:
        return {
            "key": "route_match",
            "score": 1,
            "comment": "No expected route was provided.",
        }

    return {
        "key": "route_match",
        "score": 1 if actual_route == expected_route else 0,
        "comment": f"Expected {expected_route}, got {actual_route}.",
    }


def validate_langsmith_environment() -> None:
    """Fail fast with setup guidance before calling LangSmith APIs."""
    if not os.getenv("LANGSMITH_API_KEY"):
        raise RuntimeError(
            "LANGSMITH_API_KEY is required to run LangSmith "
            "evaluation. Copy .env.example to .env, set the key, then retry."
        )


def create_or_update_dataset(client: Any, dataset_name: str = DATASET_NAME) -> str:
    """Create a small LangSmith dataset and return its name."""
    try:
        dataset = client.read_dataset(dataset_name=dataset_name)
    except Exception:
        dataset = client.create_dataset(
            dataset_name=dataset_name,
            description="Smoke evaluation set for the SORA multi-agent PoC.",
        )

    existing_examples = []
    try:
        existing_examples = list(client.list_examples(dataset_id=dataset.id))
    except Exception:
        existing_examples = []

    if not existing_examples:
        client.create_examples(
            dataset_id=dataset.id,
            inputs=[example["inputs"] for example in EVALUATION_EXAMPLES],
            outputs=[example["reference_outputs"] for example in EVALUATION_EXAMPLES],
        )

    return dataset_name


def run_langsmith_evaluation() -> Any:
    """Run the SORA graph against the LangSmith smoke dataset."""
    validate_langsmith_environment()

    try:
        from dotenv import load_dotenv
    except ImportError:
        load_dotenv = None

    if load_dotenv:
        load_dotenv()

    try:
        from langsmith import Client, evaluate
    except ImportError as exc:
        raise RuntimeError(
            "The langsmith package is required to run evaluation. "
            "Install project dependencies before running evals.py."
        ) from exc

    client = Client()
    dataset_name = create_or_update_dataset(client)

    return evaluate(
        sora_target,
        data=dataset_name,
        evaluators=[compliance_disclaimer_evaluator, route_evaluator],
        experiment_prefix=EXPERIMENT_PREFIX,
    )


if __name__ == "__main__":
    try:
        result = run_langsmith_evaluation()
    except RuntimeError as exc:
        print(f"LangSmith evaluation was not started: {exc}")
    else:
        print(result)
