import os
import sys
import time

import streamlit as st
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, os.path.dirname(__file__))

from agent.runner import run_agent
from agent.tools import _LT_KEY, _ST_KEY
from ui.components import render_step, render_memory_panel, render_analytics, render_tool_status

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Agent Systems Playground · Visakh Sankar",
    page_icon="🤖",
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
MAX_RUNS = 5

# ── Session state ──────────────────────────────────────────────────────────────
for k, v in [
    ("run_count",   0),
    ("author_mode", False),
    ("task_input",  ""),
    ("steps",       []),
    ("run_time",    0.0),
    (_LT_KEY,       {}),
    (_ST_KEY,       {}),
]:
    if k not in st.session_state:
        st.session_state[k] = v

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🤖 Agent Settings")
    st.divider()

    render_tool_status()
    st.divider()

    if st.session_state.author_mode:
        st.caption("🔓 **Author mode** — no limits active")
    else:
        remaining = MAX_RUNS - st.session_state.run_count
        st.caption(f"Runs remaining this session: **{remaining}/{MAX_RUNS}**")
        with st.expander("🔑 Author access"):
            pw = st.text_input("Password", type="password", label_visibility="collapsed")
            if pw and pw == st.secrets.get("AUTHOR_PASSWORD", ""):
                st.session_state.author_mode = True
                st.rerun()
            elif pw:
                st.caption("Incorrect password.")

    st.divider()

    with st.expander("ℹ️ How this works"):
        st.markdown(
            """
            **Agent Loop**
            1. 🧠 **Think** — agent reasons about what to do
            2. 🔧 **Act** — selects and calls a tool
            3. 👁️ **Observe** — sees the tool result
            4. ↻ Repeats until it has a final answer

            **Tools available:**
            - 🔍 Web Search (Tavily)
            - 🧮 Calculator (safe eval)
            - 💾 Remember (store facts)
            - 🗃️ Recall (retrieve facts)
            - 📋 Summarise (URL or text)

            Switch to **Multi-Agent** in the sidebar for
            orchestrator + specialist agent mode.
            """
        )

    st.divider()
    st.caption("Agent Systems Playground · v1.0")
    st.caption("by [Visakh Sankar](https://visakhsankar.com)")

# ── Header ─────────────────────────────────────────────────────────────────────
col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.markdown('<div class="hero-title">🤖 Agent Systems Playground</div>', unsafe_allow_html=True)
    st.markdown(
        '<p class="hero-sub">Watch an AI agent think, choose tools, and reason its way '
        'to an answer — every step exposed.</p>',
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

# ── Example tasks ──────────────────────────────────────────────────────────────
EXAMPLES = [
    ("🏥 Healthcare AI ROI",
     "What are the top 3 use cases for AI in healthcare in 2025, and what ROI can hospitals expect from each?"),
    ("📊 Market Research",
     "Research the current state of the RAG (Retrieval-Augmented Generation) market. Who are the key players and what are the growth projections?"),
    ("💰 Investment Calc",
     "If I invest $250,000 in an AI automation project that saves 3 FTEs at $85,000 each per year, what is the ROI and payback period?"),
    ("🔍 Competitive Intel",
     "Compare OpenAI, Anthropic, and Google Gemini as enterprise AI providers. What are the key differentiators for a Fortune 500 choosing between them?"),
]

st.markdown('<div class="section-label">Your Task</div>', unsafe_allow_html=True)

with st.expander("💡 Try an example task"):
    ex_cols = st.columns(len(EXAMPLES))
    for col, (label, text) in zip(ex_cols, EXAMPLES):
        with col:
            if st.button(label, use_container_width=True):
                st.session_state.task_input = text
                st.rerun()

task = st.text_area(
    "Describe what you want the agent to research, calculate, or analyse",
    value=st.session_state.task_input,
    height=110,
    placeholder=(
        "e.g. What are the top AI use cases in financial services, "
        "and calculate the expected ROI for a mid-sized bank investing $500k?"
    ),
    label_visibility="collapsed",
)

_, btn_col, _ = st.columns([1, 2, 1])
with btn_col:
    run = st.button("🚀  Run Agent", use_container_width=True)

# ── Run ────────────────────────────────────────────────────────────────────────
if run and task.strip():
    if not st.session_state.author_mode and st.session_state.run_count >= MAX_RUNS:
        st.warning(
            f"🔒 Demo limit reached — {MAX_RUNS} runs per session. "
            "Refresh the page to start a new session."
        )
        st.stop()

    if not (os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY", "")):
        st.error("⚠️ OPENAI_API_KEY is not set.")
        st.stop()

    # Reset for new run
    st.session_state.run_count += 1
    st.session_state.steps     = []
    st.session_state[_ST_KEY]  = {}

    st.markdown("---")
    st.markdown('<div class="section-label">🔄 Agent Loop</div>', unsafe_allow_html=True)
    st.markdown(
        f'<p style="color:#64748b;font-size:12px;margin-bottom:12px;">'
        f'Watching the agent think, act, and observe — live.</p>',
        unsafe_allow_html=True,
    )

    steps_container = st.container()
    t_start = time.time()

    for step in run_agent(task):
        st.session_state.steps.append(step)
        with steps_container:
            render_step(step, show_agent_badge=False)

    st.session_state.run_time = time.time() - t_start

elif run:
    st.warning("Please enter a task above before running the agent.")

# ── Post-run panels ────────────────────────────────────────────────────────────
if st.session_state.steps:
    st.markdown("---")
    render_analytics(st.session_state.steps, st.session_state.run_time)

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
