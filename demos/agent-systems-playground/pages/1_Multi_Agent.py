"""
Multi-Agent mode: Orchestrator → Research → Analysis → Writer.
"""
import os
import sys
import time
import pathlib

import streamlit as st
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

from agent.multi_agent import run_multi_agent, AGENTS
from agent.tools import _LT_KEY, _ST_KEY
from ui.components import render_step, render_memory_panel, render_analytics, render_tool_status

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Multi-Agent · Agent Systems Playground",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    .stApp { background-color: #f8fafc; }
    .block-container { padding-top: 1.5rem; }
    .hero-title { font-size:2.4rem;font-weight:800;color:#1e293b;line-height:1.2;margin-bottom:6px; }
    .hero-sub   { color:#64748b;font-size:1.05rem;margin-bottom:0; }
    .section-label {
        font-size:11px;color:#64748b;text-transform:uppercase;
        letter-spacing:2px;margin-bottom:8px;margin-top:4px;
    }
    div[data-testid="stButton"] > button {
        background:#3b82f6 !important;color:white !important;border:none !important;
        border-radius:8px !important;font-weight:700 !important;font-size:15px !important;
        box-shadow:0 2px 6px rgba(59,130,246,0.3) !important;
    }
    div[data-testid="stButton"] > button:hover { opacity:0.88 !important; }
    hr { border-color:#e2e8f0 !important;margin:20px 0 !important; }
    details { border:1px solid #e2e8f0 !important;border-radius:8px !important;background:#fff !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Config ─────────────────────────────────────────────────────────────────────
MAX_RUNS = 3   # multi-agent is heavier, so fewer free runs

# ── Session state ──────────────────────────────────────────────────────────────
for k, v in [
    ("ma_run_count",   0),
    ("author_mode",    False),
    ("ma_task_input",  ""),
    ("ma_steps",       []),
    ("ma_run_time",    0.0),
    (_LT_KEY,          {}),
    (_ST_KEY,          {}),
]:
    if k not in st.session_state:
        st.session_state[k] = v

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🎯 Multi-Agent Mode")
    st.divider()

    render_tool_status()
    st.divider()

    if st.session_state.author_mode:
        st.caption("🔓 **Author mode** — no limits active")
    else:
        remaining = MAX_RUNS - st.session_state.ma_run_count
        st.caption(f"Runs remaining this session: **{remaining}/{MAX_RUNS}**")
        with st.expander("🔑 Author access"):
            pw = st.text_input("Password", type="password", label_visibility="collapsed")
            if pw and pw == st.secrets.get("AUTHOR_PASSWORD", ""):
                st.session_state.author_mode = True
                st.rerun()
            elif pw:
                st.caption("Incorrect password.")

    st.divider()

    with st.expander("ℹ️ How multi-agent works"):
        for key, a in AGENTS.items():
            if key == "orchestrator":
                continue
            st.markdown(
                f"**{a['emoji']} {a['name']}**  \n"
                f"Tools: {', '.join(a.get('allowed_tools', set()))}"
            )
        st.markdown(
            """
            **Flow:**
            1. 🎯 Orchestrator plans the task
            2. Delegates to specialist agents
            3. Each agent runs its own loop
            4. Results are passed as context
            5. ✍️ Writer synthesises the final answer
            """
        )

    st.divider()
    st.caption("Agent Systems Playground · v1.0")
    st.caption("by [Visakh Sankar](https://visakhsankar.com)")

# ── Header ─────────────────────────────────────────────────────────────────────
col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.markdown('<div class="hero-title">🎯 Multi-Agent Mode</div>', unsafe_allow_html=True)
    st.markdown(
        '<p class="hero-sub">An Orchestrator breaks your task into subtasks and delegates '
        'to specialist agents — each with their own tools and reasoning loop.</p>',
        unsafe_allow_html=True,
    )
with col_h2:
    st.markdown(
        '<div style="text-align:right;padding-top:10px;">'
        '<span style="color:#94a3b8;font-size:12px;">by </span>'
        '<span style="color:#3b82f6;font-size:13px;font-weight:600;">Visakh Sankar</span>'
        '</div>',
        unsafe_allow_html=True,
    )

st.markdown("---")

# ── Agent diagram ──────────────────────────────────────────────────────────────
agent_cols = st.columns(len(AGENTS))
for col, (key, a) in zip(agent_cols, AGENTS.items()):
    with col:
        tools_str = ", ".join(a.get("allowed_tools", [])) if "allowed_tools" in a else "Planning"
        st.markdown(
            f"""
            <div style="background:{a['bg']};border:1px solid {a['border']};border-radius:10px;
                        padding:12px 14px;text-align:center;">
              <div style="font-size:24px;">{a['emoji']}</div>
              <div style="font-weight:700;font-size:13px;color:{a['color']};margin:4px 0;">
                {a['name']}</div>
              <div style="font-size:11px;color:#64748b;">{tools_str}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown("---")

# ── Example tasks ──────────────────────────────────────────────────────────────
EXAMPLES = [
    ("🌐 AI Market Report",
     "Research the global AI market size in 2025, identify the top 3 enterprise AI companies by revenue, and calculate the year-over-year growth rate if the market was $150B in 2024."),
    ("🏗️ Architecture Decision",
     "Research the pros and cons of RAG vs fine-tuning for enterprise AI. Calculate the cost difference for a company processing 1 million queries per month, and recommend the best approach."),
    ("📈 Business Case",
     "Research AI adoption rates in the insurance industry. Calculate the ROI for an insurer investing $2M in claims automation that reduces processing time by 40% on 500,000 claims per year worth $300 average cost each."),
]

st.markdown('<div class="section-label">Your Task</div>', unsafe_allow_html=True)

with st.expander("💡 Try a multi-agent example"):
    for label, text in EXAMPLES:
        if st.button(label, use_container_width=True):
            st.session_state.ma_task_input = text
            st.rerun()

task = st.text_area(
    "Task for the agent team",
    value=st.session_state.ma_task_input,
    height=110,
    placeholder=(
        "Give the agents a complex task that requires research + calculation + synthesis. "
        "e.g. Research AI in logistics, calculate ROI for a $1M investment, and write an executive summary."
    ),
    label_visibility="collapsed",
)

_, btn_col, _ = st.columns([1, 2, 1])
with btn_col:
    run = st.button("🚀  Run Agent Team", use_container_width=True)

# ── Run ────────────────────────────────────────────────────────────────────────
if run and task.strip():
    if not st.session_state.author_mode and st.session_state.ma_run_count >= MAX_RUNS:
        st.warning(
            f"🔒 Demo limit reached — {MAX_RUNS} multi-agent runs per session. "
            "Refresh the page to start a new session."
        )
        st.stop()

    if not (os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY", "")):
        st.error("⚠️ OPENAI_API_KEY is not set.")
        st.stop()

    st.session_state.ma_run_count += 1
    st.session_state.ma_steps     = []
    st.session_state[_ST_KEY]     = {}

    st.markdown("---")
    st.markdown('<div class="section-label">🔄 Multi-Agent Execution</div>', unsafe_allow_html=True)
    st.markdown(
        '<p style="color:#64748b;font-size:12px;margin-bottom:12px;">'
        'Each agent badge shows who is acting. Watch the task flow between specialists.</p>',
        unsafe_allow_html=True,
    )

    steps_container = st.container()
    t_start = time.time()

    for step in run_multi_agent(task):
        st.session_state.ma_steps.append(step)
        with steps_container:
            render_step(step, show_agent_badge=True)

    st.session_state.ma_run_time = time.time() - t_start

elif run:
    st.warning("Please enter a task above before running the agent team.")

# ── Post-run panels ────────────────────────────────────────────────────────────
if st.session_state.ma_steps:
    st.markdown("---")
    render_analytics(st.session_state.ma_steps, st.session_state.ma_run_time)

    st.markdown("---")
    render_memory_panel(
        short_term=st.session_state.get(_ST_KEY, {}),
        long_term=st.session_state.get(_LT_KEY, {}),
    )

    st.markdown(
        '<p style="color:#94a3b8;font-size:12px;text-align:center;margin-top:24px;">'
        "Built by Visakh Sankar · visakhsankar.com</p>",
        unsafe_allow_html=True,
    )
