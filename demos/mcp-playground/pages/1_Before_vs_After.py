"""Before vs After MCP — side-by-side comparison page."""
from __future__ import annotations

import os
import time

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# ─── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Before vs After MCP",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
      .block-container { padding-top: 3rem; padding-bottom: 2rem; }
      .stTextArea textarea { font-size: 14px; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ─── API Key Guard ────────────────────────────────────────────────────────────
openai_key = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY", "")
if not openai_key:
    st.error("⚠️ **OPENAI_API_KEY** is missing. Add it to your `.env` file.")
    st.stop()

openai_client = OpenAI(api_key=openai_key)

# ─── Imports (after path is valid) ───────────────────────────────────────────
import sys
import pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

from core.mcp_client import MCPClient
from core.runner import run_with_mcp, run_without_mcp
from ui.components import render_answer_card, render_protocol_message, render_section_label

# ─── Constants ────────────────────────────────────────────────────────────────
PURPLE = "#7C3AED"
TEXT = "#1e293b"
MUTED = "#64748b"
CARD_BORDER = "#e2e8f0"

# ─── Header ───────────────────────────────────────────────────────────────────
st.markdown(
    '<h1 style="font-size:2.2rem;font-weight:800;color:#1e293b;margin-bottom:2px">⚖️ Before vs After MCP</h1>',
    unsafe_allow_html=True,
)
st.markdown(
    '<p style="font-size:16px;color:#64748b;margin-bottom:2px">Same question. Without tools vs with MCP. See the difference.</p>',
    unsafe_allow_html=True,
)
st.markdown(
    '<p style="font-size:12px;color:#94a3b8">by <a href="https://visakhsankar.com" style="color:#7C3AED;text-decoration:none;font-weight:600">Visakh Sankar</a></p>',
    unsafe_allow_html=True,
)

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
          <td style="padding:9px 14px;border:1px solid #e2e8f0;text-align:center">❌ Estimates</td>
          <td style="padding:9px 14px;border:1px solid #e2e8f0;text-align:center">✅ Exact results</td>
        </tr>
        <tr>
          <td style="padding:9px 14px;border:1px solid #e2e8f0;color:#1e293b;font-weight:500">Database</td>
          <td style="padding:9px 14px;border:1px solid #e2e8f0;text-align:center">❌ No access</td>
          <td style="padding:9px 14px;border:1px solid #e2e8f0;text-align:center">✅ Live query</td>
        </tr>
        <tr style="background:#f8fafc">
          <td style="padding:9px 14px;border:1px solid #e2e8f0;color:#1e293b;font-weight:500">Accuracy</td>
          <td style="padding:9px 14px;border:1px solid #e2e8f0;text-align:center">❌ Training data only</td>
          <td style="padding:9px 14px;border:1px solid #e2e8f0;text-align:center">✅ Grounded in facts</td>
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

    st.divider()
    col_left, col_right = st.columns(2)

    # ── LEFT: Without MCP ─────────────────────────────────────────────────────
    with col_left:
        st.markdown(
            '<div style="background:#FEF2F2;border:1px solid #FECACA;border-radius:10px;padding:12px 16px;margin-bottom:16px;text-align:center">'
            '<span style="font-size:13px;font-weight:700;color:#DC2626">❌ No tools available</span>'
            '<br><span style="font-size:11px;color:#EF4444">GPT-4o-mini — training data only</span>'
            '</div>',
            unsafe_allow_html=True,
        )

        with st.spinner("Running without MCP..."):
            t0 = time.time()
            no_mcp_result = run_without_mcp(task, openai_client)
            t_no_mcp = int((time.time() - t0) * 1000)

        st.markdown(
            f'<div style="background:#ffffff;border:1px solid #e2e8f0;border-radius:8px;padding:10px 14px;margin-bottom:8px;display:flex;gap:16px;justify-content:center">'
            f'<span style="font-size:12px;color:#64748b">Tokens: <strong style="color:#1e293b">{no_mcp_result["token_count"]}</strong></span>'
            f'<span style="font-size:12px;color:#64748b">Time: <strong style="color:#1e293b">{t_no_mcp}ms</strong></span>'
            f'</div>',
            unsafe_allow_html=True,
        )

        st.markdown("**Model answer:**")
        st.markdown(
            f'<div style="background:#FFF7ED;border:1px solid #FED7AA;border-radius:10px;padding:16px 20px;font-size:14px;color:#1e293b;line-height:1.7">'
            f'{no_mcp_result["answer"].replace(chr(10), "<br>")}'
            f'</div>',
            unsafe_allow_html=True,
        )

    # ── RIGHT: With MCP ───────────────────────────────────────────────────────
    with col_right:
        st.markdown(
            '<div style="background:#F0FDF4;border:1px solid #BBF7D0;border-radius:10px;padding:12px 16px;margin-bottom:16px;text-align:center">'
            '<span style="font-size:13px;font-weight:700;color:#15803D">✅ MCP tools active</span>'
            '<br><span style="font-size:11px;color:#22C55E">GPT-4o + 5 live tools via MCP</span>'
            '</div>',
            unsafe_allow_html=True,
        )

        mcp_client = MCPClient()
        with st.spinner("Running with MCP..."):
            t1 = time.time()
            mcp_result = run_with_mcp(task, mcp_client, openai_client)
            t_mcp = int((time.time() - t1) * 1000)

        mcp_log = mcp_client.get_log()
        tool_call_count = mcp_result["tool_call_count"]

        st.markdown(
            f'<div style="background:#ffffff;border:1px solid #e2e8f0;border-radius:8px;padding:10px 14px;margin-bottom:8px;display:flex;gap:16px;justify-content:center">'
            f'<span style="font-size:12px;color:#64748b">Tool calls: <strong style="color:#7C3AED">{tool_call_count}</strong></span>'
            f'<span style="font-size:12px;color:#64748b">Messages: <strong style="color:#7C3AED">{len(mcp_log)}</strong></span>'
            f'<span style="font-size:12px;color:#64748b">Time: <strong style="color:#1e293b">{t_mcp}ms</strong></span>'
            f'</div>',
            unsafe_allow_html=True,
        )

        # Condensed protocol log
        with st.expander(f"📡 Protocol messages ({len(mcp_log)} total)", expanded=False):
            for msg in mcp_log:
                render_protocol_message(msg)

        st.markdown("**Enhanced answer:**")
        render_answer_card(mcp_result["answer"])
