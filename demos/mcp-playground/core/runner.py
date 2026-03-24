"""Agent runner: OpenAI function-calling loop bridged via MCP client."""
from __future__ import annotations

import json
from typing import Any

from core.mcp_client import MCPClient
from core.tools import get_openai_schemas


def run_with_mcp(task: str, client: MCPClient, openai_client: Any) -> dict:
    """
    Full agent loop:
    1. initialize MCP session
    2. list tools via MCP
    3. convert tool list to OpenAI schemas
    4. run GPT-4o loop with tool calls
    5. for each tool call, call MCP tools/call
    6. return {answer, steps, tool_call_count}
    """
    steps: list[str] = []
    tool_call_count = 0

    # ── 1. Handshake ──────────────────────────────────────────────────────────
    init_result = client.call("initialize", {
        "protocolVersion": "2024-11-05",
        "clientInfo": {"name": "mcp-playground-client", "version": "1.0.0"},
    })
    steps.append(f"Handshake: server {init_result['serverInfo']['name']} v{init_result['serverInfo']['version']}")

    # ── 2. Discover tools ─────────────────────────────────────────────────────
    tools_result = client.call("tools/list", {})
    available_tools = tools_result["tools"]
    steps.append(f"Discovered {len(available_tools)} tools: {', '.join(t['name'] for t in available_tools)}")

    # ── 3. Build OpenAI schemas from MCP tool list ────────────────────────────
    openai_tools = []
    for t in available_tools:
        openai_tools.append({
            "type": "function",
            "function": {
                "name": t["name"],
                "description": t["description"],
                "parameters": t["inputSchema"],
            },
        })

    # ── 4. Agent loop ─────────────────────────────────────────────────────────
    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful AI assistant with access to real-time tools via MCP. "
                "Use them to answer the user's question accurately. "
                "When calculations are needed, use the calculator tool — do not estimate. "
                "When current data is needed, use the appropriate tool."
            ),
        },
        {"role": "user", "content": task},
    ]

    MAX_ITERATIONS = 8
    for iteration in range(MAX_ITERATIONS):
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            tools=openai_tools,
            tool_choice="auto",
        )
        msg = response.choices[0].message

        if msg.tool_calls:
            messages.append(msg)
            for tc in msg.tool_calls:
                tool_name = tc.function.name
                try:
                    arguments = json.loads(tc.function.arguments)
                except json.JSONDecodeError:
                    arguments = {}

                steps.append(f"Calling tool: {tool_name}({json.dumps(arguments)[:120]})")
                tool_call_count += 1

                # ── 5. Route through MCP ──────────────────────────────────────
                tool_result = client.call("tools/call", {
                    "name": tool_name,
                    "arguments": arguments,
                })
                content_text = tool_result["content"][0]["text"]
                steps.append(f"Tool result: {content_text[:200]}{'...' if len(content_text) > 200 else ''}")

                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": content_text,
                })
        else:
            # No more tool calls — final answer
            answer = msg.content or ""
            steps.append("Final answer generated.")
            return {
                "answer": answer,
                "steps": steps,
                "tool_call_count": tool_call_count,
            }

    # Fallback if loop maxed out
    last_content = messages[-1].get("content", "") if isinstance(messages[-1], dict) else ""
    return {
        "answer": last_content or "Agent reached maximum iterations without a final answer.",
        "steps": steps,
        "tool_call_count": tool_call_count,
    }


def run_without_mcp(task: str, openai_client: Any) -> dict:
    """
    Simple GPT-4o-mini call with no tools.
    Returns {answer, token_count}.
    """
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful AI assistant. Answer as best you can from your training data.",
            },
            {"role": "user", "content": task},
        ],
        max_tokens=600,
    )
    msg = response.choices[0].message
    usage = response.usage
    return {
        "answer": msg.content or "",
        "token_count": usage.total_tokens if usage else 0,
    }
