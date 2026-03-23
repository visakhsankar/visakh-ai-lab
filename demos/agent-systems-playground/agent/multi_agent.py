"""
Multi-agent orchestration: Orchestrator → Research → Analysis → Writer.
Uses raw OpenAI function calling; yields step dicts with agent labels.
"""
import json
import os
import time
from typing import Generator

import streamlit as st
from openai import OpenAI

from agent.tools import execute_tool
from agent.runner import TOOL_DEFINITIONS, SYSTEM_PROMPT, MAX_ITERATIONS

# ── Agent registry ─────────────────────────────────────────────────────────────

AGENTS = {
    "orchestrator": {
        "name": "Orchestrator",
        "emoji": "🎯",
        "color": "#3B82F6",
        "bg":    "#EFF6FF",
        "border":"#BFDBFE",
        "system": (
            "You are an AI orchestration agent. Your job is to analyse the user's task, "
            "create a clear execution plan, and delegate subtasks to specialist agents. "
            "Be specific in your instructions to each specialist."
        ),
    },
    "research": {
        "name": "Research Agent",
        "emoji": "🔍",
        "color": "#059669",
        "bg":    "#F0FDF4",
        "border":"#BBF7D0",
        "system": (
            "You are a research specialist. Gather accurate, current information using web search. "
            "Search multiple times if needed. Always ground your findings in real sources."
        ),
        "allowed_tools": {"web_search", "summarise", "remember"},
    },
    "analysis": {
        "name": "Analysis Agent",
        "emoji": "🧮",
        "color": "#D97706",
        "bg":    "#FEF3C7",
        "border":"#FDE68A",
        "system": (
            "You are a quantitative analysis specialist. Perform precise calculations and draw "
            "data-driven conclusions. Always show your workings using the calculator. "
            "Pull relevant context from memory."
        ),
        "allowed_tools": {"calculator", "recall", "remember"},
    },
    "writer": {
        "name": "Writer Agent",
        "emoji": "✍️",
        "color": "#7C3AED",
        "bg":    "#FAF5FF",
        "border":"#DDD6FE",
        "system": (
            "You are a synthesis and writing specialist. Take all research findings and analysis "
            "results and produce a clear, well-structured final answer. Recall any stored facts. "
            "Be comprehensive but concise."
        ),
        "allowed_tools": {"recall", "summarise"},
    },
}


# ── Client ─────────────────────────────────────────────────────────────────────

def _client() -> OpenAI:
    key = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY", "")
    return OpenAI(api_key=key)


# ── Sub-agent runner ───────────────────────────────────────────────────────────

def _run_sub_agent(agent_key: str, subtask: str) -> Generator[dict, None, None]:
    """Run one specialist agent loop; yields step dicts labelled with agent_key."""
    client = _client()
    agent  = AGENTS[agent_key]
    allowed = agent.get("allowed_tools", set())

    agent_tools = [
        t for t in TOOL_DEFINITIONS
        if t["function"]["name"] in allowed
    ] if allowed else None

    messages = [
        {"role": "system", "content": agent["system"]},
        {"role": "user",   "content": subtask},
    ]

    for _ in range(MAX_ITERATIONS):
        t0 = time.time()
        try:
            kwargs = dict(
                model="gpt-4o",
                messages=messages,
                max_tokens=1200,
            )
            if agent_tools:
                kwargs["tools"] = agent_tools
                kwargs["tool_choice"] = "auto"

            response = client.chat.completions.create(**kwargs)
        except Exception as e:
            yield {"type": "error", "content": str(e), "time_ms": 0, "agent": agent_key}
            return

        elapsed = int((time.time() - t0) * 1000)
        msg = response.choices[0].message

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

        if not msg.tool_calls:
            yield {"type": "done", "content": msg.content or "", "time_ms": elapsed, "agent": agent_key}
            return

        if msg.content and msg.content.strip():
            yield {"type": "think", "content": msg.content.strip(), "time_ms": elapsed, "agent": agent_key}

        for tc in msg.tool_calls:
            tool_name = tc.function.name
            try:
                tool_args = json.loads(tc.function.arguments)
            except Exception:
                tool_args = {}

            yield {"type": "act",     "tool": tool_name, "inputs": tool_args, "time_ms": 0,        "agent": agent_key}
            t1 = time.time()
            result   = execute_tool(tool_name, tool_args)
            tool_ms  = int((time.time() - t1) * 1000)
            yield {"type": "observe", "tool": tool_name, "output": result,    "time_ms": tool_ms,   "agent": agent_key}
            messages.append({"role": "tool", "tool_call_id": tc.id, "content": result})

    yield {"type": "error", "content": "Max iterations reached.", "time_ms": 0, "agent": agent_key}


# ── Orchestrator ───────────────────────────────────────────────────────────────

_PLAN_PROMPT = """\
Task: {task}

Create an execution plan. Output ONLY valid JSON:
{{
  "analysis": "1-2 sentence summary of what this task requires",
  "steps": [
    {{"agent": "research",  "subtask": "specific research instruction"}},
    {{"agent": "analysis",  "subtask": "specific analysis instruction based on research"}},
    {{"agent": "writer",    "subtask": "synthesise all findings into a final answer"}}
  ]
}}

Rules:
- Use only agents: research, analysis, writer
- writer MUST be the last step
- Only include analysis step if calculations are genuinely needed
- Be specific in each subtask instruction\
"""


def run_multi_agent(task: str) -> Generator[dict, None, None]:
    """
    Run the full multi-agent workflow.
    Yields step dicts; each has an 'agent' key identifying who produced it.
    """
    client = _client()

    # ── Step 1: Orchestrator plans ────────────────────────────────────────────
    yield {
        "type": "think",
        "content": "Analysing task and creating an execution plan for the specialist agents…",
        "time_ms": 0,
        "agent": "orchestrator",
    }

    t0 = time.time()
    try:
        plan_resp = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": AGENTS["orchestrator"]["system"]},
                {"role": "user",   "content": _PLAN_PROMPT.format(task=task)},
            ],
            response_format={"type": "json_object"},
            max_tokens=600,
        )
        plan = json.loads(plan_resp.choices[0].message.content)
    except Exception:
        plan = {
            "analysis": "Running all agents on the task.",
            "steps": [
                {"agent": "research", "subtask": task},
                {"agent": "writer",   "subtask": f"Write a final answer for: {task}"},
            ],
        }

    elapsed = int((time.time() - t0) * 1000)

    yield {
        "type": "plan",
        "content": plan.get("analysis", ""),
        "steps":   plan.get("steps", []),
        "time_ms": elapsed,
        "agent":   "orchestrator",
    }

    # ── Step 2: Execute planned steps ─────────────────────────────────────────
    agent_results: dict[str, str] = {}

    for step in plan.get("steps", []):
        agent_key = step.get("agent", "research")
        if agent_key not in AGENTS:
            continue

        base_subtask = step.get("subtask", task)

        # Inject prior agents' findings as context
        if agent_results:
            context_lines = "\n".join(
                f"[{k.upper()} AGENT RESULT]\n{v}"
                for k, v in agent_results.items()
            )
            subtask = f"{base_subtask}\n\nContext from previous agents:\n{context_lines}"
        else:
            subtask = base_subtask

        # Orchestrator delegates
        yield {
            "type":         "delegate",
            "content":      f"Delegating to {AGENTS[agent_key]['name']}: {base_subtask[:120]}",
            "target_agent": agent_key,
            "time_ms":      0,
            "agent":        "orchestrator",
        }

        # Run the sub-agent
        final_output = ""
        for sub_step in _run_sub_agent(agent_key, subtask):
            yield sub_step
            if sub_step["type"] == "done":
                final_output = sub_step["content"]

        agent_results[agent_key] = final_output

    # ── Step 3: Orchestrator wraps up ─────────────────────────────────────────
    yield {
        "type":    "orchestrator_done",
        "content": "All specialist agents have completed their tasks. Final answer is above (Writer Agent).",
        "time_ms": 0,
        "agent":   "orchestrator",
    }
