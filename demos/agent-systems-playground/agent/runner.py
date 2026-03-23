"""
Single-agent loop using raw OpenAI function calling.
Yields step dicts so the UI can render them live.
"""
import json
import os
import time
from typing import Generator

import streamlit as st
from openai import OpenAI

from agent.tools import execute_tool

# ── Client ─────────────────────────────────────────────────────────────────────

def _client() -> OpenAI:
    key = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY", "")
    return OpenAI(api_key=key)


# ── Tool definitions (OpenAI function-calling format) ─────────────────────────

TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": (
                "Search the web for current, real-time information. "
                "Use for facts, data, news, statistics, or anything requiring up-to-date knowledge."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Specific search query — be precise for better results."},
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": (
                "Evaluate a mathematical expression precisely. "
                "Use for any arithmetic, percentages, ROI, or formula. Never estimate numbers you can compute."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {"type": "string", "description": "e.g. '(1800000 - 500000) / 500000 * 100'"},
                },
                "required": ["expression"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "remember",
            "description": "Store an important fact or finding in long-term memory for future reference in this or future sessions.",
            "parameters": {
                "type": "object",
                "properties": {
                    "key":   {"type": "string", "description": "Short label, e.g. 'user_industry' or 'roi_result'"},
                    "value": {"type": "string", "description": "The fact or value to store"},
                },
                "required": ["key", "value"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "recall",
            "description": "Retrieve facts previously stored in long-term memory. Leave key empty to get everything.",
            "parameters": {
                "type": "object",
                "properties": {
                    "key": {"type": "string", "description": "Memory key, or empty string for all memories"},
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "summarise",
            "description": "Summarise a URL or a long piece of text into 3-5 clear bullet points.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url_or_text": {"type": "string", "description": "URL to fetch and summarise, or raw text to condense"},
                },
                "required": ["url_or_text"],
            },
        },
    },
]

SYSTEM_PROMPT = """\
You are an expert AI research and analysis agent. You have access to tools — use them.

Your approach:
1. THINK through exactly what you need before acting
2. SEARCH for real information — never hallucinate facts
3. CALCULATE precisely — use the calculator for any numbers
4. REMEMBER key findings so they persist
5. SYNTHESISE a clear, structured final answer

Always explain your reasoning briefly before calling a tool.\
"""

MAX_ITERATIONS = 12


# ── Step dict schema ───────────────────────────────────────────────────────────
# {
#   type:    "think" | "act" | "observe" | "done" | "error"
#   content: str          (think text or final answer or error message)
#   tool:    str | None   (tool name for act/observe)
#   inputs:  dict | None  (tool args for act)
#   output:  str | None   (tool result for observe)
#   time_ms: int
#   agent:   str          ("main" for single-agent)
# }


# ── Agent loop ─────────────────────────────────────────────────────────────────

def run_agent(task: str, prior_messages: list | None = None) -> Generator[dict, None, None]:
    """
    Run the single-agent loop. Yields step dicts live.
    prior_messages: existing conversation history (optional, for follow-up tasks).
    """
    client = _client()

    if prior_messages:
        messages = prior_messages + [{"role": "user", "content": task}]
    else:
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": task},
        ]

    for _ in range(MAX_ITERATIONS):
        t0 = time.time()
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                tools=TOOL_DEFINITIONS,
                tool_choice="auto",
                max_tokens=1500,
            )
        except Exception as e:
            yield {"type": "error", "content": str(e), "time_ms": 0, "agent": "main"}
            return

        elapsed = int((time.time() - t0) * 1000)
        msg = response.choices[0].message

        # Build serialisable message dict
        msg_dict: dict = {"role": "assistant"}
        if msg.content:
            msg_dict["content"] = msg.content
        if msg.tool_calls:
            msg_dict["tool_calls"] = [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {"name": tc.function.name, "arguments": tc.function.arguments},
                }
                for tc in msg.tool_calls
            ]
        messages.append(msg_dict)

        # No tool calls → final answer
        if not msg.tool_calls:
            yield {
                "type": "done",
                "content": msg.content or "Task complete.",
                "time_ms": elapsed,
                "agent": "main",
            }
            return

        # Emit thinking text if present
        if msg.content and msg.content.strip():
            yield {
                "type": "think",
                "content": msg.content.strip(),
                "time_ms": elapsed,
                "agent": "main",
            }

        # Execute each tool call
        for tc in msg.tool_calls:
            tool_name = tc.function.name
            try:
                tool_args = json.loads(tc.function.arguments)
            except Exception:
                tool_args = {}

            yield {"type": "act", "tool": tool_name, "inputs": tool_args, "time_ms": 0, "agent": "main"}

            t1 = time.time()
            result = execute_tool(tool_name, tool_args)
            tool_ms = int((time.time() - t1) * 1000)

            yield {"type": "observe", "tool": tool_name, "output": result, "time_ms": tool_ms, "agent": "main"}

            messages.append({"role": "tool", "tool_call_id": tc.id, "content": result})

    yield {
        "type": "error",
        "content": f"Reached the maximum of {MAX_ITERATIONS} iterations without a final answer.",
        "time_ms": 0,
        "agent": "main",
    }
