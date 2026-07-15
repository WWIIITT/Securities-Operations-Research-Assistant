from __future__ import annotations

from typing import Any

from .tools import get_stock_data as stock_tool
from .tools import search_compliance_policy as compliance_tool

TOOL_NAMES = ("get_stock_data", "search_compliance_policy")

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    FastMCP = None


def _invoke_langchain_tool(tool_obj: Any, payload: dict[str, Any]) -> dict[str, Any]:
    if hasattr(tool_obj, "invoke"):
        return tool_obj.invoke(payload)
    return tool_obj(**payload)


if FastMCP is not None:
    mcp = FastMCP("sora-local-tools")

    @mcp.tool(name="get_stock_data")
    def get_stock_data(ticker: str) -> dict[str, Any]:
        """Fetch current stock data and basic company information."""
        return _invoke_langchain_tool(stock_tool, {"ticker": ticker})

    @mcp.tool(name="search_compliance_policy")
    def search_compliance_policy(query: str) -> dict[str, Any]:
        """Search the local compliance RAG policy store."""
        return _invoke_langchain_tool(compliance_tool, {"query": query})
else:
    mcp = None


def main() -> None:
    """Run the local stdio MCP server."""
    if mcp is None:
        raise RuntimeError("The mcp package is required to run the SORA MCP server.")
    mcp.run()


if __name__ == "__main__":
    main()
