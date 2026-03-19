import os
import sys
import streamlit as st
from dotenv import load_dotenv

# Load .env if present (local dev)
load_dotenv()

# Ensure local imports resolve
sys.path.insert(0, os.path.dirname(__file__))

from core.extractor import extract_constraints
from core.recommender import stream_reasoning, get_structured_recommendation, load_pattern_library
from ui.components import (
    render_constraint_tags,
    render_radar_chart,
    render_pattern_card,
    render_why_not_table,
    render_architecture_brief,
)

# ─── Page config ─────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Architecture Simulator · Visakh Sankar",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── Global CSS ──────────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    .stApp { background-color: #f8fafc; }

    .hero-title {
        font-size: 2.6rem;
        font-weight: 800;
        color: #1e293b;
        line-height: 1.2;
        margin-bottom: 6px;
    }
    .hero-title span {
        color: #3b82f6;
    }
    .hero-sub {
        color: #64748b;
        font-size: 1.05rem;
        margin-bottom: 0;
    }
    .section-label {
        font-size: 11px;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-bottom: 10px;
        margin-top: 4px;
    }
    .reasoning-box {
        background: linear-gradient(135deg, #f8fafc, #f1f5f9);
        border: 1px solid #e2e8f0;
        border-left: 4px solid #3b82f6;
        border-radius: 10px;
        padding: 20px 24px;
        font-size: 14px;
        line-height: 1.75;
        color: #1e293b;
        min-height: 140px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.04);
    }
    /* text-area */
    .stTextArea textarea {
        background-color: #ffffff !important;
        color: #1e293b !important;
        border: 1.5px solid #e2e8f0 !important;
        border-radius: 8px !important;
        font-size: 15px !important;
    }
    /* primary button */
    div[data-testid="stButton"] > button[kind="primary"],
    div[data-testid="stButton"] > button {
        background: #3b82f6 !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        font-size: 15px !important;
        padding: 12px 0 !important;
        letter-spacing: 0.3px;
        box-shadow: 0 2px 6px rgba(59,130,246,0.3) !important;
    }
    div[data-testid="stButton"] > button:hover { opacity: 0.88 !important; }

    /* expander */
    details { border: 1px solid #e2e8f0 !important; border-radius: 8px !important; background: #fff !important; }

    /* divider */
    hr { border-color: #e2e8f0 !important; margin: 24px 0 !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ─── Header ───────────────────────────────────────────────────────────────────────
col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.markdown(
        '<div class="hero-title">🏗️ AI Architecture Simulator</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p class="hero-sub">Describe your enterprise use case → get an expert architecture '
        'recommendation with live reasoning, trade-off analysis, and an architecture brief.</p>',
        unsafe_allow_html=True,
    )
with col_h2:
    st.markdown(
        '<div style="text-align:right;padding-top:8px;">'
        '<span style="color:#94a3b8;font-size:12px;">by </span>'
        '<span style="color:#3b82f6;font-size:13px;font-weight:600;">Visakh Sankar</span>'
        "</div>",
        unsafe_allow_html=True,
    )

st.markdown("---")

# ─── Example use cases ───────────────────────────────────────────────────────────
EXAMPLES = [
    (
        "🏥 Healthcare",
        "We're a 500-person healthcare company. Our doctors need to query clinical guidelines and drug "
        "interaction databases in real time. We cannot send any patient data to external cloud APIs due "
        "to HIPAA requirements. Our ML team has 2 engineers with intermediate experience.",
    ),
    (
        "💸 Fintech Startup",
        "Early-stage fintech startup, 10 engineers total (1 ML). We need a chatbot that answers "
        "questions about our product docs and FAQs. Budget is very tight, and we need to ship in 2 weeks.",
    ),
    (
        "🚚 Enterprise Logistics",
        "Enterprise logistics company. We need to query across contract documents, live shipment data "
        "in our SQL database, and real-time web data. Large team, budget is not a constraint. "
        "Accuracy and reliability are critical.",
    ),
    (
        "⚖️ Legal",
        "Large law firm. We need to search 10,000+ case documents and find complex relationships "
        "between entities like clients, cases, judges, and legal precedents. Our team includes "
        "2 data engineers but no ML specialists.",
    ),
]

# ─── Session state defaults ───────────────────────────────────────────────────────
if "user_input" not in st.session_state:
    st.session_state.user_input = ""
if "result_ready" not in st.session_state:
    st.session_state.result_ready = False

# ─── Input ────────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-label">Your Use Case</div>', unsafe_allow_html=True)

with st.expander("💡 Try an example"):
    ex_cols = st.columns(len(EXAMPLES))
    for col, (label, text) in zip(ex_cols, EXAMPLES):
        with col:
            if st.button(label, use_container_width=True):
                st.session_state.user_input = text
                st.rerun()

user_input = st.text_area(
    "Describe your use case",
    value=st.session_state.user_input,
    height=130,
    placeholder=(
        "e.g. We're a healthcare company. Our doctors need to query clinical guidelines. "
        "Data cannot leave our servers due to HIPAA. Small ML team of 2 engineers…"
    ),
    label_visibility="collapsed",
)

_, btn_col, _ = st.columns([1, 2, 1])
with btn_col:
    analyze = st.button("🔍  Analyze & Recommend Architecture", use_container_width=True)

# ─── Analysis ─────────────────────────────────────────────────────────────────────
if analyze and user_input.strip():
    if not os.environ.get("OPENAI_API_KEY"):
        st.error("⚠️  OPENAI_API_KEY is not set. Add it to your `.env` file or environment.")
        st.stop()

    patterns = load_pattern_library()
    st.markdown("---")

    # Step 1 — Extract constraints
    with st.spinner("🔍  Extracting constraints from your description…"):
        constraints = extract_constraints(user_input)

    st.markdown('<div class="section-label">Extracted Constraints</div>', unsafe_allow_html=True)
    render_constraint_tags(constraints)

    if constraints.get("constraints_summary"):
        st.markdown(
            f'<p style="color:#64748b;font-size:13px;margin-top:10px;font-style:italic;">'
            f'"{constraints["constraints_summary"]}"</p>',
            unsafe_allow_html=True,
        )

    if constraints.get("key_requirements"):
        with st.expander("📌 Full requirements extracted"):
            for req in constraints["key_requirements"]:
                st.markdown(f"• {req}")

    st.markdown("---")

    # Step 2 — Stream reasoning
    st.markdown('<div class="section-label">🧠  Architect\'s Reasoning</div>', unsafe_allow_html=True)
    st.markdown(
        '<p style="color:#64748b;font-size:12px;margin-bottom:8px;">'
        "Live reasoning — watch the architecture decision unfold.</p>",
        unsafe_allow_html=True,
    )

    reasoning_placeholder = st.empty()
    full_reasoning = ""

    for token in stream_reasoning(constraints, patterns):
        full_reasoning += token
        reasoning_placeholder.markdown(
            f'<div class="reasoning-box">{full_reasoning}</div>',
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # Step 3 — Structured recommendation
    with st.spinner("📊  Preparing recommendation and charts…"):
        structured = get_structured_recommendation(constraints, patterns)

    pattern_map = {p["id"]: p for p in patterns}
    rec_id      = structured.get("recommended", {}).get("pattern_id", "")
    rec_pattern = pattern_map.get(rec_id)

    if not rec_pattern:
        st.error("Could not find the recommended pattern in the library. Please try again.")
        st.stop()

    # ── Cards + Radar chart ──────────────────────────────────────────────────────
    col_cards, col_chart = st.columns([1.1, 1])

    with col_cards:
        st.markdown('<div class="section-label">Recommendation</div>', unsafe_allow_html=True)
        render_pattern_card(rec_pattern, structured, rank=1)

        for alt in structured.get("alternatives", []):
            alt_pattern = pattern_map.get(alt.get("pattern_id", ""))
            if alt_pattern:
                render_pattern_card(alt_pattern, structured, rank=alt.get("rank", 2))

    with col_chart:
        st.markdown('<div class="section-label">Trade-off Comparison (top 3)</div>', unsafe_allow_html=True)

        radar_patterns = [rec_pattern]
        radar_names    = [rec_pattern["name"]]
        for alt in structured.get("alternatives", [])[:2]:
            p = pattern_map.get(alt.get("pattern_id", ""))
            if p:
                radar_patterns.append(p)
                radar_names.append(p["name"])

        fig = render_radar_chart(radar_patterns, radar_names)
        st.plotly_chart(fig, use_container_width=True)

        # Score legend
        st.markdown(
            '<p style="color:#94a3b8;font-size:11px;text-align:center;">'
            "All axes 1–5 (higher = better). Scores reflect suitability to your constraints.</p>",
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # ── Why NOT the others ───────────────────────────────────────────────────────
    if structured.get("rejected"):
        render_why_not_table(structured["rejected"], patterns)
        st.markdown("---")

    # ── Architecture Brief ───────────────────────────────────────────────────────
    render_architecture_brief(rec_pattern, constraints, structured)

    st.markdown(
        '<p style="color:#94a3b8;font-size:12px;text-align:center;margin-top:24px;">'
        "Built by Visakh Sankar · visakhsankar.com</p>",
        unsafe_allow_html=True,
    )

elif analyze:
    st.warning("Please describe your use case above before clicking Analyze.")
