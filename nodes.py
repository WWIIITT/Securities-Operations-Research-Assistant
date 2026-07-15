from __future__ import annotations

import re
from typing import Any

from llm import build_chat_model, message_content
from market_symbols import MARKET_SYMBOL_ALIASES, resolve_market_symbol
from mcp_client import call_tool
from state import AgentState

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


def _invoke_llm(system_prompt: str, user_prompt: str) -> str:
    model = build_chat_model()
    response = model.invoke(
        [
            ("system", system_prompt),
            ("human", user_prompt),
        ]
    )
    return message_content(response)


def _claims_no_realtime_access(text: str) -> bool:
    lowered = (text or "").lower()
    patterns = [
        "do not have real-time",
        "don't have real-time",
        "do not have access to real-time",
        "no real-time data access",
        "as of my last update",
        "knowledge cutoff",
    ]
    return any(pattern in lowered for pattern in patterns)


def _deterministic_route(user_text: str, state: AgentState) -> tuple[str, str]:
    lowered = user_text.lower()
    words = set(re.findall(r"[a-zA-Z]+", lowered))
    ticker = extract_ticker(user_text)

    has_market_signal = bool(ticker) or bool(words & MARKET_KEYWORDS)
    has_compliance_signal = bool(words & COMPLIANCE_KEYWORDS)
    route = MARKET_ROUTE if has_market_signal and not (has_compliance_signal and not ticker) else COMPLIANCE_ROUTE
    return route, ticker or state.get("ticker", "")


def extract_ticker(text: str) -> str:
    """Extract a likely equity ticker from a user query."""
    normalized_text = (text or "").upper()
    for alias in sorted(MARKET_SYMBOL_ALIASES, key=len, reverse=True):
        if re.search(rf"(?<![A-Z0-9]){re.escape(alias)}(?![A-Z0-9])", normalized_text):
            return MARKET_SYMBOL_ALIASES[alias]["yfinance_symbol"]

    cashtag = re.search(r"\$([A-Za-z]{1,5})(?=\b)", text)
    if cashtag:
        return resolve_market_symbol(cashtag.group(1))["yfinance_symbol"]

    explicit = re.search(r"\b(?:ticker|stock|index|price of)\s*:?\s*([A-Za-z0-9^.-]{1,8})\b", text, re.IGNORECASE)
    if explicit:
        candidate = resolve_market_symbol(explicit.group(1))["yfinance_symbol"]
        if candidate not in NON_TICKER_WORDS:
            return candidate

    for candidate in re.findall(r"\b[A-Z]{1,6}\d{0,3}\b", text):
        resolved = resolve_market_symbol(candidate)["yfinance_symbol"]
        if candidate.upper() not in NON_TICKER_WORDS:
            return resolved

    return ""


def router_node(state: AgentState) -> dict[str, Any]:
    """Route the user request to market analysis or compliance review."""
    user_text = _latest_user_text(state)
    fallback_route, ticker = _deterministic_route(user_text, state)
    try:
        llm_route = _invoke_llm(
            "You route securities operations queries. Respond with exactly "
            "'market_analysis' or 'compliance_check'.",
            f"User query: {user_text}",
        ).strip().lower()
        route = llm_route if llm_route in {MARKET_ROUTE, COMPLIANCE_ROUTE} else fallback_route
    except Exception:
        route = fallback_route

    return {
        "route": route,
        "ticker": ticker,
        "compliance_status": f"Routed to {route}.",
    }


def analyst_node(state: AgentState) -> dict[str, Any]:
    """Call the market data tool and write a concise analyst report."""
    user_text = _latest_user_text(state)
    ticker = state.get("ticker") or extract_ticker(user_text)

    stock_result = call_tool("get_stock_data", {"ticker": ticker})
    normalized_ticker = stock_result.get("ticker") or ticker

    fallback_report = (
        "Market Analyst Report\n"
        f"Requested symbol: {stock_result.get('requested_symbol') or ticker or 'Unavailable'}\n"
        f"Ticker: {normalized_ticker or 'Unavailable'}\n"
        f"Status: {'Data available' if stock_result.get('status') == 'ok' else 'Data unavailable'}\n"
        f"Company: {stock_result.get('company_name', 'Not available')}\n"
        f"Current price: {stock_result.get('current_price', 'Not available')} {stock_result.get('currency') or ''}\n"
        f"Previous close: {stock_result.get('previous_close', 'Not available')}\n"
        f"Market cap: {stock_result.get('market_cap', 'Not available')}\n"
        f"Sector: {stock_result.get('sector', 'Not available')}\n"
        f"Business summary: {stock_result.get('summary') or stock_result.get('message') or 'Not available.'}"
    )
    try:
        report = _invoke_llm(
            "You are SORA's Market Analyst. Write a concise, factual market report. "
            "Use the provided market tool output as the source of current market data. "
            "Do not say you lack real-time data when the tool output status is ok. "
            "Do not provide investment advice and do not guarantee returns.",
            f"User query: {user_text}\nMarket tool output: {stock_result}",
        ) or fallback_report
        if stock_result.get("status") == "ok" and _claims_no_realtime_access(report):
            report = fallback_report
    except Exception:
        report = fallback_report

    return {
        "ticker": normalized_ticker or "",
        "analyst_report": report,
        "messages": [{"role": "assistant", "content": report}],
    }


def reviewer_node(state: AgentState) -> dict[str, Any]:
    """Retrieve compliance rules and finalize the report with required disclosures."""
    base_report = state.get("analyst_report") or _latest_user_text(state)
    search_query = base_report or "financial promotions risk disclosure guaranteed returns"
    compliance_result = call_tool("search_compliance_policy", {"query": search_query})
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
    try:
        review_text = _invoke_llm(
            "You are SORA's Compliance Reviewer. Review the report against the retrieved "
            "rules. Be concise and never remove the mandatory disclosures.",
            f"Report:\n{base_report}\n\nRetrieved rules:\n{rule_lines}",
        )
    except Exception:
        review_text = "Compliance review completed using deterministic fallback."

    final_report = (
        f"{base_report}\n\n"
        "Compliance Review\n"
        f"{review_text}\n\n"
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
