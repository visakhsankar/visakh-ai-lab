"""MCP client with JSON-RPC 2.0 message logging."""
from __future__ import annotations

import time
from typing import Any

from core.mcp_server import MCPServer


class MCPClient:
    """Client that wraps MCPServer and logs every request/response pair."""

    def __init__(self):
        self._server = MCPServer()
        self._log: list[dict] = []
        self._id_counter = 0

    # ── Public API ────────────────────────────────────────────────────────────

    def call(self, method: str, params: dict | None = None) -> dict:
        """Build a JSON-RPC 2.0 request, call the server, log both, return result."""
        if params is None:
            params = {}

        self._id_counter += 1
        req_id = self._id_counter

        request_payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": req_id,
        }

        t0 = time.time()
        self._log.append({
            "direction": "request",
            "method": method,
            "payload": request_payload,
            "timestamp_ms": int(t0 * 1000),
            "duration_ms": None,
        })

        try:
            result = self._server.handle(method, params)
            error = None
        except Exception as e:
            result = None
            error = {"code": -32603, "message": str(e)}

        duration_ms = int((time.time() - t0) * 1000)

        if error is not None:
            response_payload = {
                "jsonrpc": "2.0",
                "error": error,
                "id": req_id,
            }
        else:
            response_payload = {
                "jsonrpc": "2.0",
                "result": result,
                "id": req_id,
            }

        self._log.append({
            "direction": "response",
            "method": method,
            "payload": response_payload,
            "timestamp_ms": int(time.time() * 1000),
            "duration_ms": duration_ms,
        })

        if error is not None:
            raise RuntimeError(error["message"])

        return result

    def get_log(self) -> list[dict]:
        """Return a copy of all logged messages."""
        return list(self._log)

    def clear_log(self):
        """Clear the message log and reset ID counter."""
        self._log = []
        self._id_counter = 0
