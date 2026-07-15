from __future__ import annotations

from typing import Any

import nodes
from nodes import COMPLIANCE_ROUTE, MARKET_ROUTE
from state import AgentState


def _route_from_state(state: AgentState) -> str:
    return state.get("route") or COMPLIANCE_ROUTE


def _merge_state(current: dict[str, Any], update: dict[str, Any]) -> dict[str, Any]:
    merged = dict(current)
    update_messages = update.get("messages")
    if update_messages:
        merged["messages"] = [*(merged.get("messages") or []), *update_messages]
    for key, value in update.items():
        if key != "messages":
            merged[key] = value
    return merged


class SimpleSoraGraph:
    """Small fallback with the same invoke shape used by compiled LangGraph apps."""

    def invoke(self, state: AgentState) -> dict[str, Any]:
        current: dict[str, Any] = dict(state)
        current = _merge_state(current, nodes.router_node(current))
        if current.get("route") == MARKET_ROUTE:
            current = _merge_state(current, nodes.analyst_node(current))
        current = _merge_state(current, nodes.reviewer_node(current))
        return current


def build_graph() -> Any:
    """Build the SORA workflow, using LangGraph when installed."""
    try:
        from langgraph.graph import END, START, StateGraph
    except ImportError:
        return SimpleSoraGraph()

    workflow = StateGraph(AgentState)
    workflow.add_node("router", nodes.router_node)
    workflow.add_node("analyst", nodes.analyst_node)
    workflow.add_node("reviewer", nodes.reviewer_node)

    workflow.add_edge(START, "router")
    workflow.add_conditional_edges(
        "router",
        _route_from_state,
        {
            MARKET_ROUTE: "analyst",
            COMPLIANCE_ROUTE: "reviewer",
        },
    )
    workflow.add_edge("analyst", "reviewer")
    workflow.add_edge("reviewer", END)

    return workflow.compile()


app = build_graph()
