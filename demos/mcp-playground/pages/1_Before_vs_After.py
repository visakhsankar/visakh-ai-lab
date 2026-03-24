"""Before vs After MCP — side-by-side comparison page."""
from __future__ import annotations

import os
import sys
import pathlib
import time

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

from core.mcp_client import MCPClient
from core.runner import run_with_mcp, run_without_mcp
from ui.components import render_answer_card, render_protocol_message, render_section_label

# ─── Constants ────────────────────────────────────────────────────────────────
PURPLE = "#7C3AED"
TEXT = "#1e293b"
MUTED = "#64748b"
CARD_BORDER = "#e2e8f0"
MAX_COMPARES = 5

# ─── Session State ─────────────────────────────────────────────────────────────
if "bva_count" not in st.session_state:
    st.session_state.bva_count = 0
if "author_mode" not in st.session_state:
    st.session_state.author_mode = False

# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚖️ Before vs After")
    st.divider()

    runs_left = MAX_COMPARES - st.session_state.bva_count
    runs_display = "∞" if st.session_state.author_mode else str(max(runs_left, 0))
    limit_label = "∞" if st.session_state.author_mode else str(MAX_COMPARES)

    st.markdown(
        f'<div style="text-align:center;padding:10px;background:#EDE9FE;border:1px solid #C4B5FD;border-radius:8px"><span style="font-size:22px;font-weight:800;color:#7C3AED">{runs_display}</span><span style="font-size:12px;color:#6D28D9;font-weight:600"> / {limit_label} compares</span></div>',
        unsafe_allow_html=True,
    )

    st.divider()

    with st.expander("🔑 Author Access"):
        pw_input = st.text_input("Password", type="password", key="bva_author_pw")
        if st.button("Unlock", key="bva_unlock_btn"):
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
            st.success("✅ Author mode active — unlimited compares")

# ─── API Key Guard ────────────────────────────────────────────────────────────
openai_key = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY", "")
if not openai_key:
    st.error("⚠️ **OPENAI_API_KEY** is missing. Add it to your `.env` file.")
    st.stop()

openai_client = OpenAI(api_key=openai_key)

st.markdown(
    """
    <style>
      .block-container { padding-top: 3rem; padding-bottom: 2rem; }
      .stTextArea textarea { font-size: 14px; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ─── Header ───────────────────────────────────────────────────────────────────
st.markdown('<h1 style="font-size:2.2rem;font-weight:800;color:#1e293b;margin-bottom:2px">⚖️ Before vs After MCP</h1>', unsafe_allow_html=True)
st.markdown('<p style="font-size:16px;color:#64748b;margin-bottom:2px">Same question. Without tools vs with MCP. See the difference.</p>', unsafe_allow_html=True)
st.markdown('<p style="font-size:12px;color:#94a3b8">by <a href="https://visakhsankar.com" style="color:#7C3AED;text-decoration:none;font-weight:600">Visakh Sankar</a></p>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─── Comparison Table ─────────────────────────────────────────────────────────
st.markdown(
    """
    <table style="width:100%;border-collapse:collapse;font-size:13px;margin-bottom:16px">
      <thead>
        <tr style="background:#f8fafc">
          <th style="padding:10px 14px;text-align:left;border:1px solid #e2e8f0;color:#64748b;font-weight:700;text-transform:uppercase;letter-spacing:0.5px">Capability</th>
          <th style="padding:10px 14px;text-align:center;border:1px solid #e2e8f0;color:#ef4444;font-weight:700">Without MCP</th>
          <th style="padding:10px 14px;text-align:center;border:1px solid #e2e8f0;color:#22c55e;font-weight:700">With MCP</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td style="padding:9px 14px;border:1px solid #e2e8f0;color:#1e293b;font-weight:500">Web access</td>
          <td style="padding:9px 14px;border:1px solid #e2e8f0;text-align:center">❌ Training data only</td>
          <td style="padding:9px 14px;border:1px solid #e2e8f0;text-align:center">✅ Real-time search</td>
        </tr>
        <tr style="background:#f8fafc">
          <td style="padding:9px 14px;border:1px solid #e2e8f0;color:#1e293b;font-weight:500">Calculations</td>
          <td style="padding:9px 14px;border:1px solid #e2e8f0;text-align:center">❌ Estimates only</td>
          <td style="padding:9px 14px;border:1px solid #e2e8f0;text-align:center">✅ Exact results</td>
        </tr>
        <tr>
          <td style="padding:9px 14px;border:1px solid #e2e8f0;color:#1e293b;font-weight:500">Database queries</td>
          <td style="padding:9px 14px;border:1px solid #e2e8f0;text-align:center">❌ No access</td>
          <td style="padding:9px 14px;border:1px solid #e2e8f0;text-align:center">✅ Live query</td>
        </tr>
        <tr style="background:#f8fafc">
          <td style="padding:9px 14px;border:1px solid #e2e8f0;color:#1e293b;font-weight:500">Factual accuracy</td>
          <td style="padding:9px 14px;border:1px solid #e2e8f0;text-align:center">❌ May hallucinate</td>
          <td style="padding:9px 14px;border:1px solid #e2e8f0;text-align:center">✅ Grounded in live data</td>
        </tr>
      </tbody>
    </table>
    """,
    unsafe_allow_html=True,
)

# ─── Task Input ───────────────────────────────────────────────────────────────
render_section_label("ENTER YOUR TASK", "We'll run the exact same question through both approaches.")

EXAMPLE_TASKS = [
    "Which region had the highest revenue growth from Q1 to Q4? Calculate the exact percentage.",
    "What is the total annual revenue across all regions and which product has the best NPS score?",
    "What is the current temperature difference between London and Tokyo?",
]

with st.expander("💡 Good comparison tasks"):
    for ex in EXAMPLE_TASKS:
        st.markdown(f"• {ex}")

task_input = st.text_area(
    "Task",
    placeholder="e.g. Which region had the highest revenue growth from Q1 to Q4? Calculate the exact percentage.",
    height=90,
    label_visibility="collapsed",
    key="bva_task",
)

col_l, col_c, col_r = st.columns([2, 1, 2])
with col_c:
    compare_btn = st.button("⚖️ Compare", use_container_width=True, type="primary")

# ─── Comparison Run ───────────────────────────────────────────────────────────
if compare_btn:
    task = task_input.strip()
    if not task:
        st.warning("Please enter a task first.")
        st.stop()

    can_run = st.session_state.author_mode or (st.session_state.bva_count < MAX_COMPARES)
    if not can_run:
        st.error(f"You've used all {MAX_COMPARES} comparisons for this session. Refresh to start over or unlock author mode.")
        st.stop()

    st.session_state.bva_count += 1

    st.divider()
    col_left, col_right = st.columns(2)

    # ── LEFT: Without MCP ─────────────────────────────────────────────────────
    with col_left:
        st.markdown('<div style="background:#FEF2F2;border:1px solid #FECACA;border-radius:10px;padding:12px 16px;margin-bottom:16px;text-align:center"><span style="font-size:13px;font-weight:700;color:#DC2626">❌ No tools available</span><br><span style="font-size:11px;color:#EF4444">GPT-4o-mini — training data only</span></div>', unsafe_allow_html=True)

        with st.spinner("Running without MCP..."):
            t0 = time.time()
            no_mcp_result = run_without_mcp(task, openai_client)
            t_no_mcp = int((time.time() - t0) * 1000)

        st.markdown(
            f'<div style="background:#ffffff;border:1px solid #e2e8f0;border-radius:8px;padding:10px 14px;margin-bottom:8px;display:flex;gap:16px;justify-content:center"><span style="font-size:12px;color:#64748b">Tokens: <strong style="color:#1e293b">{no_mcp_result["token_count"]}</strong></span><span style="font-size:12px;color:#64748b">Time: <strong style="color:#1e293b">{t_no_mcp}ms</strong></span></div>',
            unsafe_allow_html=True,
        )

        st.markdown("**Model answer:**")
        escaped = no_mcp_result["answer"].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br>")
        st.markdown(
            f'<div style="background:#FFF7ED;border:1px solid #FED7AA;border-radius:10px;padding:16px 20px;font-size:14px;color:#1e293b;line-height:1.7">{escaped}</div>',
            unsafe_allow_html=True,
        )

    # ── RIGHT: With MCP ───────────────────────────────────────────────────────
    with col_right:
        st.markdown('<div style="background:#F0FDF4;border:1px solid #BBF7D0;border-radius:10px;padding:12px 16px;margin-bottom:16px;text-align:center"><span style="font-size:13px;font-weight:700;color:#15803D">✅ MCP tools active</span><br><span style="font-size:11px;color:#22C55E">GPT-4o + 5 live tools via MCP</span></div>', unsafe_allow_html=True)

        mcp_client = MCPClient()
        with st.spinner("Running with MCP..."):
            t1 = time.time()
            mcp_result = run_with_mcp(task, mcp_client, openai_client)
            t_mcp = int((time.time() - t1) * 1000)

        mcp_log = mcp_client.get_log()
        tool_call_count = mcp_result["tool_call_count"]

        st.markdown(
            f'<div style="background:#ffffff;border:1px solid #e2e8f0;border-radius:8px;padding:10px 14px;margin-bottom:8px;display:flex;gap:16px;justify-content:center"><span style="font-size:12px;color:#64748b">Tool calls: <strong style="color:#7C3AED">{tool_call_count}</strong></span><span style="font-size:12px;color:#64748b">Messages: <strong style="color:#7C3AED">{len(mcp_log)}</strong></span><span style="font-size:12px;color:#64748b">Time: <strong style="color:#1e293b">{t_mcp}ms</strong></span></div>',
            unsafe_allow_html=True,
        )

        with st.expander(f"📡 Protocol messages ({len(mcp_log)} total)", expanded=False):
            for msg in mcp_log:
                render_protocol_message(msg)

        st.markdown("**Enhanced answer:**")
        render_answer_card(mcp_result["answer"])

    # ─── Why the difference? ──────────────────────────────────────────────────
    st.divider()
    st.markdown(
        '<div style="background:#F5F3FF;border:1px solid #DDD6FE;border-radius:12px;padding:20px 24px;margin-top:8px"><div style="font-size:13px;font-weight:800;color:#7C3AED;text-transform:uppercase;letter-spacing:1px;margin-bottom:10px">Why is there a difference?</div><div style="font-size:13px;color:#1e293b;line-height:1.7">Without MCP, the AI is answering purely from memory — its training data has a cutoff and it cannot access any live systems. It may guess, estimate, or confabulate.<br><br>With MCP, the AI runs a protocol handshake, discovers what tools are available, and dynamically routes requests to the right tool. The answer is grounded in real-time data fetched during your query — not training data.</div></div>',
        unsafe_allow_html=True,
    )
