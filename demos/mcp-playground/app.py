"""MCP Playground — JSON-RPC 2.0 protocol inspector for AI tool connections."""
from __future__ import annotations

import os
import sys
import time

sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

from core.mcp_client import MCPClient
from core.runner import run_with_mcp
from core.tools import TOOL_REGISTRY
from ui.components import (
    render_answer_card,
    render_architecture_diagram,
    render_protocol_message,
    render_section_label,
    render_stats_row,
    render_tool_registry,
)

load_dotenv()

# ─── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="MCP Playground",
    page_icon="🔌",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
      .block-container { padding-top: 3rem; padding-bottom: 2rem; }
      [data-testid="stMetricValue"] { font-size: 1.6rem; font-weight: 700; }
      [data-testid="stMetricLabel"] { font-size: 0.75rem; color: #64748b; }
      .stTextArea textarea { font-size: 14px; }
      h1 { color: #1e293b; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ─── Config ───────────────────────────────────────────────────────────────────
MAX_RUNS = 5

# ─── Session State (must be before sidebar) ───────────────────────────────────
if "run_count" not in st.session_state:
    st.session_state.run_count = 0
if "author_mode" not in st.session_state:
    st.session_state.author_mode = False
if "mcp_log" not in st.session_state:
    st.session_state.mcp_log = []
if "last_answer" not in st.session_state:
    st.session_state.last_answer = ""
if "last_steps" not in st.session_state:
    st.session_state.last_steps = []
if "call_counts" not in st.session_state:
    st.session_state.call_counts = {name: 0 for name in TOOL_REGISTRY}
if "active_tool" not in st.session_state:
    st.session_state.active_tool = ""

# ─── API Key Guard ────────────────────────────────────────────────────────────
openai_key = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY", "")
tavily_key = os.getenv("TAVILY_API_KEY") or st.secrets.get("TAVILY_API_KEY", "")

if not openai_key:
    st.error("⚠️ **OPENAI_API_KEY** is missing. Add it to your `.env` file and restart.")
    st.stop()

if not tavily_key:
    st.warning("⚠️ **TAVILY_API_KEY** is missing. Web search tool will not work. Other tools are still available.")

openai_client = OpenAI(api_key=openai_key)

# ─── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Agent Settings")
    st.divider()

    st.markdown("**🔧 Available Tools**")
    render_tool_registry(TOOL_REGISTRY, st.session_state.call_counts, st.session_state.active_tool)

    st.divider()

    runs_left = MAX_RUNS - st.session_state.run_count
    if st.session_state.author_mode:
        runs_left_display = "∞"
    else:
        runs_left_display = str(max(runs_left, 0))

    st.markdown(
        f'<div style="text-align:center;padding:10px;background:#EDE9FE;border:1px solid #C4B5FD;border-radius:8px">'
        f'<span style="font-size:22px;font-weight:800;color:#7C3AED">{runs_left_display}</span>'
        f'<span style="font-size:12px;color:#6D28D9;font-weight:600"> / {MAX_RUNS if not st.session_state.author_mode else "∞"} runs</span>'
        f'</div>',
        unsafe_allow_html=True,
    )

    st.divider()

    with st.expander("🔑 Author Access"):
        pw_input = st.text_input("Password", type="password", key="author_pw")
        if st.button("Unlock", key="unlock_btn"):
            try:
                correct = st.secrets.get("AUTHOR_PASSWORD", "")
            except Exception:
                correct = os.getenv("AUTHOR_PASSWORD", "")
            if pw_input == correct and correct:
                st.session_state.author_mode = True
                st.success("Author mode enabled!")
            else:
                st.error("Incorrect password.")
        if st.session_state.author_mode:
            st.success("✅ Author mode active — unlimited runs")

    with st.expander("ℹ️ How MCP Works"):
        st.markdown(
            """
            **Model Context Protocol (MCP)** is an open standard for connecting AI models to external tools and data sources.

            **The flow:**
            1. **Host** (your app) starts a session
            2. **Client** sends JSON-RPC 2.0 requests
            3. **Server** handles requests and routes to tools
            4. **Tools** execute and return results

            **Why JSON-RPC 2.0?**
            - Language-agnostic wire format
            - Request/Response IDs for matching
            - Standardised error codes

            This demo shows every single message — the "network inspector" for AI tools.
            """
        )

# ─── Header ───────────────────────────────────────────────────────────────────
st.markdown(
    '<h1 style="font-size:2.2rem;font-weight:800;color:#1e293b;margin-bottom:2px">🔌 MCP Playground</h1>',
    unsafe_allow_html=True,
)
st.markdown(
    '<p style="font-size:16px;color:#64748b;margin-bottom:2px">Watch AI connect to the world — protocol exposed.</p>',
    unsafe_allow_html=True,
)
st.markdown(
    '<p style="font-size:12px;color:#94a3b8;margin-bottom:0">by <a href="https://visakhsankar.com" style="color:#7C3AED;text-decoration:none;font-weight:600">Visakh Sankar</a></p>',
    unsafe_allow_html=True,
)
st.markdown("<br>", unsafe_allow_html=True)

# ─── Architecture Diagram (idle state) ───────────────────────────────────────
arch_placeholder = st.empty()
with arch_placeholder:
    render_architecture_diagram("idle")

st.divider()

# ─── Task Section ─────────────────────────────────────────────────────────────
render_section_label("YOUR TASK", "Enter a question and watch every protocol message fly.")

EXAMPLE_TASKS = [
    "What are the top AI trends in 2025 and what is the temperature difference between London and Tokyo right now?",
    "Which region had the highest revenue growth from Q1 to Q4? Calculate the exact percentage.",
    "Search for recent news about Claude AI and give me a summary of the key themes.",
    "What is the total annual revenue across all regions and which product has the best NPS score?",
]

with st.expander("💡 Example tasks — click to copy"):
    for i, ex in enumerate(EXAMPLE_TASKS, 1):
        st.markdown(f"**{i}.** {ex}")

task_input = st.text_area(
    "Your task",
    placeholder="Ask anything that might require web search, calculations, weather data, or database queries...",
    height=100,
    label_visibility="collapsed",
    key="task_input",
)

# Centered button
col_l, col_c, col_r = st.columns([2, 1, 2])
with col_c:
    run_btn = st.button("🚀 Connect & Run", use_container_width=True, type="primary")

# ─── Run Logic ────────────────────────────────────────────────────────────────
if run_btn:
    task = task_input.strip()
    if not task:
        st.warning("Please enter a task first.")
        st.stop()

    can_run = st.session_state.author_mode or (st.session_state.run_count < MAX_RUNS)
    if not can_run:
        st.error(f"You've used all {MAX_RUNS} runs for this session. Refresh the page to start over, or unlock author mode.")
        st.stop()

    # Reset state
    st.session_state.mcp_log = []
    st.session_state.last_answer = ""
    st.session_state.last_steps = []
    st.session_state.call_counts = {name: 0 for name in TOOL_REGISTRY}
    st.session_state.active_tool = ""
    st.session_state.run_count += 1

    client = MCPClient()

    # ── Phase 1: Handshake ────────────────────────────────────────────────────
    arch_placeholder.empty()
    with arch_placeholder:
        render_architecture_diagram("handshake")

    with st.spinner("Initialising MCP session..."):
        client.call("initialize", {
            "protocolVersion": "2024-11-05",
            "clientInfo": {"name": "mcp-playground-client", "version": "1.0.0"},
        })

    # ── Phase 2: Discovery ────────────────────────────────────────────────────
    arch_placeholder.empty()
    with arch_placeholder:
        render_architecture_diagram("discovery")

    with st.spinner("Discovering tools..."):
        tools_result = client.call("tools/list", {})

    # ── Phase 3: Agent loop (calling + answering) ─────────────────────────────
    arch_placeholder.empty()
    with arch_placeholder:
        render_architecture_diagram("calling")

    t_start = time.time()
    with st.spinner("AI is working — tool calls in flight..."):
        # Run remaining loop (initialize and tools/list already called above)
        # Build new client that shares state but has pre-seeded calls
        # Actually: re-run with a fresh client to get the full loop in runner
        fresh_client = MCPClient()
        result = run_with_mcp(task, fresh_client, openai_client)

    t_total_ms = int((time.time() - t_start) * 1000)

    # ── Phase 4: Done ─────────────────────────────────────────────────────────
    arch_placeholder.empty()
    with arch_placeholder:
        render_architecture_diagram("answering")

    # Merge logs from both clients (setup client + runner client)
    full_log = client.get_log() + fresh_client.get_log()
    st.session_state.mcp_log = full_log
    st.session_state.last_answer = result["answer"]
    st.session_state.last_steps = result["steps"]

    # Update call counts from runner log
    for entry in fresh_client.get_log():
        if entry["direction"] == "request" and entry["method"] == "tools/call":
            tool_name = entry["payload"].get("params", {}).get("name", "")
            if tool_name in st.session_state.call_counts:
                st.session_state.call_counts[tool_name] += 1

    st.rerun()

# ─── Results Section ──────────────────────────────────────────────────────────
if st.session_state.last_answer:
    st.divider()

    # Protocol Inspector
    render_section_label(
        "PROTOCOL INSPECTOR",
        "Every JSON-RPC 2.0 message between the AI host and MCP server — nothing hidden.",
    )

    log = st.session_state.mcp_log
    tool_call_msgs = [m for m in log if m.get("method") == "tools/call" and m.get("direction") == "request"]
    resp_msgs = [m for m in log if m.get("direction") == "response"]
    total_time_ms = sum(m.get("duration_ms", 0) or 0 for m in log)

    render_stats_row(len(log), len(tool_call_msgs), total_time_ms)

    for msg in log:
        render_protocol_message(msg)

    st.divider()

    # Answer
    render_section_label("FINAL ANSWER")
    render_answer_card(st.session_state.last_answer)

    # Steps summary
    if st.session_state.last_steps:
        with st.expander("📋 Agent steps"):
            for i, step in enumerate(st.session_state.last_steps, 1):
                st.markdown(f"{i}. {step}")
