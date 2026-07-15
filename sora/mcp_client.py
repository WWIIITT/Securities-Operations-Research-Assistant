from __future__ import annotations

import asyncio
import json
import os
import sys
from typing import Any

from .tools import get_crypto_price, get_stock_data, search_compliance_policy

LOCAL_TOOLS = {
    "get_stock_data": get_stock_data,
    "get_crypto_price": get_crypto_price,
    "search_compliance_policy": search_compliance_policy,
}


def _mcp_enabled() -> bool:
    return os.getenv("MCP_ENABLED", "true").strip().lower() in {"1", "true", "yes", "on"}


def _local_call(name: str, payload: dict[str, Any]) -> dict[str, Any]:
    tool_obj = LOCAL_TOOLS[name]
    if hasattr(tool_obj, "invoke"):
        return tool_obj.invoke(payload)
    return tool_obj(**payload)


def _parse_mcp_result(result: Any) -> dict[str, Any]:
    content_items = getattr(result, "content", None) or []
    if not content_items:
        return {"status": "error", "message": "MCP tool returned no content."}

    first = content_items[0]
    text = getattr(first, "text", None)
    if text is None:
        return {"status": "error", "message": f"Unsupported MCP content: {first!r}"}

    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        return {"status": "ok", "message": text}
    return parsed if isinstance(parsed, dict) else {"status": "ok", "result": parsed}


async def _call_tool_via_mcp(name: str, payload: dict[str, Any]) -> dict[str, Any]:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client

    command = os.getenv("MCP_SERVER_COMMAND", sys.executable)
    args_text = os.getenv("MCP_SERVER_ARGS", "-m sora.mcp_server")
    args = [part for part in args_text.split(" ") if part]
    timeout = float(os.getenv("MCP_TIMEOUT_SECONDS", "8"))

    server_params = StdioServerParameters(command=command, args=args)

    async def run_call() -> dict[str, Any]:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(name, payload)
                return _parse_mcp_result(result)

    return await asyncio.wait_for(run_call(), timeout=timeout)


def call_tool(name: str, payload: dict[str, Any]) -> dict[str, Any]:
    """Call a SORA tool through MCP when available, otherwise use local fallback."""
    if name not in LOCAL_TOOLS:
        return {"status": "error", "message": f"Unknown SORA tool: {name}"}

    if not _mcp_enabled():
        return _local_call(name, payload)

    try:
        return asyncio.run(_call_tool_via_mcp(name, payload))
    except Exception as exc:
        fallback = _local_call(name, payload)
        fallback.setdefault("mcp_fallback_reason", str(exc))
        return fallback
