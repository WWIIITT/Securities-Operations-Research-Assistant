from __future__ import annotations

import re
from typing import Any

from state import AgentState
from tools import get_stock_data, search_compliance_policy

MARKET_ROUTE = "market_analysis"
COMPLIANCE_ROUTE = "compliance_check"

MARKET_KEYWORDS = {
    "analyze",
    "analysis",
    "market",
    "price",
    "quote",
    "share",
    "stock",
    "ticker",
}
COMPLIANCE_KEYWORDS = {
    "advice",
    "compliance",
    "disclose",
    "disclaimer",
    "guarantee",
    "guaranteed",
    "policy",
    "promise",
    "risk",
    "rule",
}
NON_TICKER_WORDS = MARKET_KEYWORDS | COMPLIANCE_KEYWORDS | {
    "A",
    "AI",
    "AN",
    "AND",
    "CAN",
    "DO",
    "FOR",
    "I",
    "IS",
    "IT",
    "LLM",
    "OR",
    "RAG",
    "THE",
    "TO",
    "US",
    "WE",
}


def _latest_user_text(state: AgentState) -> str:
    messages = state.get("messages") or []
    if not messages:
        return ""

    for message in reversed(messages):
        if isinstance(message, str):
            return message
        if isinstance(message, dict):
            content = message.get("content")
            if content:
                return str(content)
        content = getattr(message, "content", None)
        if content:
            return str(content)

    return ""


def _invoke_tool(tool_obj: Any, payload: dict[str, Any]) -> dict[str, Any]:
    if hasattr(tool_obj, "invoke"):
        return tool_obj.invoke(payload)
    return tool_obj(**payload)


def extract_ticker(text: str) -> str:
    """Extract a likely equity ticker from a user query."""
    cashtag = re.search(r"\$([A-Za-z]{1,5})(?=\b)", text)
    if cashtag:
        return cashtag.group(1).upper()

    explicit = re.search(r"\b(?:ticker|stock)\s*:?\s*([A-Za-z]{1,5})\b", text, re.IGNORECASE)
    if explicit:
        candidate = explicit.group(1).upper()
        if candidate not in NON_TICKER_WORDS:
            return candidate

    for candidate in re.findall(r"\b[A-Z]{1,5}\b", text):
        if candidate.upper() not in NON_TICKER_WORDS:
            return candidate.upper()

    return ""


def router_node(state: AgentState) -> dict[str, Any]:
    """Route the user request to market analysis or compliance review."""
    user_text = _latest_user_text(state)
    lowered = user_text.lower()
    words = set(re.findall(r"[a-zA-Z]+", lowered))
    ticker = extract_ticker(user_text)

    has_market_signal = bool(ticker) or bool(words & MARKET_KEYWORDS)
    has_compliance_signal = bool(words & COMPLIANCE_KEYWORDS)
    route = MARKET_ROUTE if has_market_signal and not (has_compliance_signal and not ticker) else COMPLIANCE_ROUTE

    return {
        "route": route,
        "ticker": ticker or state.get("ticker", ""),
        "compliance_status": f"Routed to {route}.",
    }


def analyst_node(state: AgentState) -> dict[str, Any]:
    """Call the market data tool and write a concise analyst report."""
    user_text = _latest_user_text(state)
    ticker = state.get("ticker") or extract_ticker(user_text)

    stock_result = _invoke_tool(get_stock_data, {"ticker": ticker})
    normalized_ticker = stock_result.get("ticker") or ticker

    if stock_result.get("status") != "ok":
        report = (
            "Market Analyst Report\n"
            f"Ticker: {normalized_ticker or 'Unavailable'}\n"
            "Status: Data unavailable\n"
            f"Reason: {stock_result.get('message', 'No market data returned.')}"
        )
    else:
        report = (
            "Market Analyst Report\n"
            f"Company: {stock_result.get('company_name')}\n"
            f"Ticker: {normalized_ticker}\n"
            f"Current price: {stock_result.get('current_price')} {stock_result.get('currency') or ''}\n"
            f"Previous close: {stock_result.get('previous_close')}\n"
            f"Market cap: {stock_result.get('market_cap')}\n"
            f"Sector: {stock_result.get('sector')}\n"
            f"Business summary: {stock_result.get('summary') or 'Not available.'}"
        )

    return {
        "ticker": normalized_ticker or "",
        "analyst_report": report,
        "messages": [{"role": "assistant", "content": report}],
    }


def reviewer_node(state: AgentState) -> dict[str, Any]:
    """Retrieve compliance rules and finalize the report with required disclosures."""
    base_report = state.get("analyst_report") or _latest_user_text(state)
    search_query = base_report or "financial promotions risk disclosure guaranteed returns"
    compliance_result = _invoke_tool(search_compliance_policy, {"query": search_query})
    rules = compliance_result.get("rules") or []

    if not rules:
        rules = [
            {
                "content": "Always disclose risks and never guarantee returns.",
                "metadata": {"rule_id": "FALLBACK-RULE"},
            }
        ]

    rule_lines = [
        f"- {rule.get('metadata', {}).get('rule_id', 'RULE')}: {rule.get('content')}"
        for rule in rules
    ]
    final_report = (
        f"{base_report}\n\n"
        "Compliance Review\n"
        "Retrieved policy rules:\n"
        f"{chr(10).join(rule_lines)}\n\n"
        "Risk disclosure: Securities prices may fluctuate, and investors may lose principal. "
        "Returns are not guaranteed. This output is for research support only and is not investment advice."
    )

    return {
        "analyst_report": final_report,
        "compliance_status": "approved_with_disclosures",
        "messages": [{"role": "assistant", "content": final_report}],
    }
