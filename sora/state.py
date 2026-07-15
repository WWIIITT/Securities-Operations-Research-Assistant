from __future__ import annotations

from typing import Annotated, Any, TypedDict

try:
    from langgraph.graph.message import add_messages
except ImportError:  # Allows static checks before project dependencies are installed.
    def add_messages(left: list[Any], right: list[Any]) -> list[Any]:
        return [*left, *right]


class AgentState(TypedDict, total=False):
    """Shared state passed between SORA LangGraph nodes."""

    messages: Annotated[list[Any], add_messages]
    route: str
    ticker: str
    analyst_report: str
    compliance_status: str
