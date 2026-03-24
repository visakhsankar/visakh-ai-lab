"""Mock MCP server implementing JSON-RPC 2.0 in-process (no subprocess)."""
from __future__ import annotations

from core.tools import TOOL_REGISTRY


class MCPServer:
    """In-process MCP server that handles JSON-RPC 2.0 method calls."""

    SERVER_INFO = {
        "name": "mcp-playground-server",
        "version": "1.0.0",
    }

    CAPABILITIES = {
        "tools": {"listChanged": False},
    }

    def handle(self, method: str, params: dict) -> dict:
        """Dispatch a JSON-RPC method call and return the result dict."""
        if method == "initialize":
            return self._initialize(params)
        if method == "tools/list":
            return self._tools_list(params)
        if method == "tools/call":
            return self._tools_call(params)
        raise ValueError(f"Unknown method: {method}")

    # ── Method handlers ───────────────────────────────────────────────────────

    def _initialize(self, params: dict) -> dict:
        return {
            "protocolVersion": "2024-11-05",
            "serverInfo": self.SERVER_INFO,
            "capabilities": self.CAPABILITIES,
        }

    def _tools_list(self, params: dict) -> dict:
        tools = []
        for tool in TOOL_REGISTRY.values():
            tools.append({
                "name": tool["name"],
                "description": tool["description"],
                "inputSchema": tool["input_schema"],
            })
        return {"tools": tools}

    def _tools_call(self, params: dict) -> dict:
        name = params.get("name", "")
        arguments = params.get("arguments", {})

        tool = TOOL_REGISTRY.get(name)
        if tool is None:
            raise ValueError(f"Tool not found: {name}")

        result = tool["fn"](**arguments)
        return {
            "content": [
                {"type": "text", "text": str(result)}
            ]
        }
