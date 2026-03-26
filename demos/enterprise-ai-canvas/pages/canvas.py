"""Enterprise AI Canvas — main capability canvas page."""
from __future__ import annotations
import os
import time
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

from core.capabilities import CAPABILITY_REGISTRY, LAYER_REGISTRY, get_layers_ordered, get_caps_for_layer
from core.constraints import CONSTRAINT_REGISTRY, signals_to_constraints
from core.analyzer import analyze_problem
from core.recommender import score_all, get_status, detect_pattern, evaluate_interrogation, STATUS_RECOMMENDED, STATUS_AVAILABLE, STATUS_NOT_RECOMMENDED, STATUS_MANUALLY_ADDED, STATUS_MANUALLY_REMOVED
from ui.components import (
    render_header, render_analysis_summary, render_constraint_card,
    render_capability_card, render_layer_header, render_pattern_badge,
    render_architecture_summary, render_signal_chips,
)

TEAL = "#0F766E"
TEAL_LIGHT = "#F0FDFA"
TEAL_BORDER = "#99F6E4"
TEXT = "#1e293b"
MUTED = "#64748b"
MAX_ANALYSES = 5

st.markdown("""
<style>
  .block-container { padding-top: 3rem; padding-bottom: 2rem; }
  .stTextArea textarea { font-size: 14px; }
</style>
""", unsafe_allow_html=True)

# ─── Session State ────────────────────────────────────────────────────────────
defaults = {
    "analysis": None,
    "signals": [],
    "active_constraints": set(),
    "scores": {},
    "manually_added": set(),
    "manually_removed": set(),
    "interrogating": None,
    "interrog_answers": {},
    "show_not_recommended": {},
    "analysis_count": 0,
    "author_mode": False,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ─── API Key ──────────────────────────────────────────────────────────────────
openai_key = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY", "")
if not openai_key:
    st.error("⚠️ **OPENAI_API_KEY** missing. Add it to .env and restart.")
    st.stop()
openai_client = OpenAI(api_key=openai_key)

# ─── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🏗️ Canvas Settings")
    st.divider()

    runs_left = MAX_ANALYSES - st.session_state.analysis_count
    runs_display = "∞" if st.session_state.author_mode else str(max(runs_left, 0))
    limit_label = "∞" if st.session_state.author_mode else str(MAX_ANALYSES)

    st.markdown(
        f'<div style="text-align:center;padding:10px;background:{TEAL_LIGHT};border:1px solid {TEAL_BORDER};border-radius:8px"><span style="font-size:22px;font-weight:800;color:{TEAL}">{runs_display}</span><span style="font-size:12px;color:{TEAL};font-weight:600"> / {limit_label} analyses</span></div>',
        unsafe_allow_html=True,
    )

    st.divider()

    if st.session_state.analysis:
        st.markdown("**Active Constraints**")
        cats = {}
        for cid in st.session_state.active_constraints:
            c = CONSTRAINT_REGISTRY.get(cid)
            if c:
                cats.setdefault(c["category"], []).append(cid)
        if cats:
            for cat, cids in sorted(cats.items()):
                st.markdown(f'<div style="font-size:11px;font-weight:700;color:{MUTED};text-transform:uppercase;letter-spacing:0.5px;margin:8px 0 4px">{cat}</div>', unsafe_allow_html=True)
                for cid in cids:
                    c = CONSTRAINT_REGISTRY[cid]
                    is_hard = c["type"] == "hard"
                    badge = "🔴" if is_hard else "🟡"
                    st.markdown(f'<div style="font-size:11px;color:{TEXT};padding:3px 0">{badge} {c["label"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<p style="font-size:12px;color:{MUTED}">No constraints detected yet.</p>', unsafe_allow_html=True)
        st.divider()

    with st.expander("🔑 Author Access"):
        pw = st.text_input("Password", type="password", key="canvas_pw")
        if st.button("Unlock", key="canvas_unlock"):
            try:
                correct = st.secrets.get("AUTHOR_PASSWORD", "")
            except Exception:
                correct = os.getenv("AUTHOR_PASSWORD", "")
            if pw == correct and correct:
                st.session_state.author_mode = True
                st.success("Author mode enabled!")
            else:
                st.error("Incorrect password.")
        if st.session_state.author_mode:
            st.success("✅ Unlimited analyses")

# ─── Header ───────────────────────────────────────────────────────────────────
render_header()

# ─── Problem Input ────────────────────────────────────────────────────────────
st.markdown(f'<div style="font-size:11px;font-weight:800;color:{TEAL};text-transform:uppercase;letter-spacing:1.5px;margin-bottom:8px">YOUR PROBLEM STATEMENT</div>', unsafe_allow_html=True)

EXAMPLES = [
    "A global bank wants to automate Tier 1 customer support across 12 markets. Must comply with GDPR and MAS regulations. Data cannot leave the EU or APAC regions.",
    "A healthcare startup is building an AI assistant for doctors to query patient records and clinical guidelines. HIPAA compliance required.",
    "An e-commerce company wants to build a product recommendation and search system for 10 million users. Must handle 50K queries per second at peak.",
    "A law firm wants to build an internal knowledge base assistant to search 20 years of case files, contracts, and legal precedents.",
    "A SaaS company is building an AI coding assistant as a product feature, to be exposed as an API to their developer customers.",
]

with st.expander("💡 Example problems — click to copy"):
    for ex in EXAMPLES:
        st.markdown(f"• {ex}")

problem_input = st.text_area(
    "Problem",
    placeholder="Describe the business problem, industry, scale, compliance requirements, users, and constraints...",
    height=120,
    label_visibility="collapsed",
    key="problem_input",
)

col_l, col_c, col_r = st.columns([2, 1, 2])
with col_c:
    analyse_btn = st.button("🔍 Analyse & Build", use_container_width=True, type="primary")

# ─── Analysis Logic ───────────────────────────────────────────────────────────
if analyse_btn:
    problem = problem_input.strip()
    if not problem:
        st.warning("Please describe your problem first.")
        st.stop()

    can_run = st.session_state.author_mode or (st.session_state.analysis_count < MAX_ANALYSES)
    if not can_run:
        st.error(f"You've used all {MAX_ANALYSES} analyses. Refresh or unlock author mode.")
        st.stop()

    st.session_state.analysis_count += 1
    st.session_state.manually_added = set()
    st.session_state.manually_removed = set()
    st.session_state.interrogating = None
    st.session_state.interrog_answers = {}

    with st.spinner("Analysing your problem with GPT-4o..."):
        analysis = analyze_problem(problem, openai_client)

    signals = analysis.get("signals", [])
    constraints = signals_to_constraints(signals)
    scores = score_all(signals)

    st.session_state.analysis = analysis
    st.session_state.signals = signals
    st.session_state.active_constraints = set(constraints)
    st.session_state.scores = scores
    st.rerun()

# ─── Canvas (rendered after analysis) ────────────────────────────────────────
if st.session_state.analysis:
    render_analysis_summary(st.session_state.analysis)

    # Pattern badge
    pattern = detect_pattern(st.session_state.scores, st.session_state.manually_added, st.session_state.manually_removed)
    render_pattern_badge(pattern)

    st.divider()

    # Constraint toggles
    with st.expander(f"⚙️ Active Constraints ({len(st.session_state.active_constraints)}) — click to toggle", expanded=False):
        st.markdown(f'<p style="font-size:13px;color:{MUTED};margin-bottom:12px">Toggle constraints to see how the capability model changes.</p>', unsafe_allow_html=True)
        constraint_changed = False
        for cat in ["Compliance", "Technical", "Business", "Operational"]:
            cat_constraints = {cid: c for cid, c in CONSTRAINT_REGISTRY.items() if c["category"] == cat and cid in st.session_state.active_constraints}
            all_cat = {cid: c for cid, c in CONSTRAINT_REGISTRY.items() if c["category"] == cat}
            if all_cat:
                st.markdown(f'<div style="font-size:12px;font-weight:700;color:{TEXT};text-transform:uppercase;margin:12px 0 4px">{cat}</div>', unsafe_allow_html=True)
                for cid, c in all_cat.items():
                    is_active = cid in st.session_state.active_constraints
                    render_constraint_card(cid, c, is_active)
                    toggled = st.toggle(f"Active", value=is_active, key=f"toggle_{cid}")
                    if toggled != is_active:
                        if toggled:
                            st.session_state.active_constraints.add(cid)
                        else:
                            st.session_state.active_constraints.discard(cid)
                        constraint_changed = True

        if constraint_changed:
            # Rebuild signals from active constraints - approximate by re-scoring
            # (Re-score with current signals, not recalculating from constraints)
            # For the live toggle, just trigger a re-score
            st.session_state.scores = score_all(st.session_state.signals)
            st.rerun()

    st.divider()

    # ─── Capability Canvas ────────────────────────────────────────────────────
    st.markdown(f'<div style="font-size:11px;font-weight:800;color:{TEAL};text-transform:uppercase;letter-spacing:1.5px;margin-bottom:4px">CAPABILITY CANVAS</div>', unsafe_allow_html=True)
    st.markdown(f'<p style="font-size:13px;color:{MUTED};margin-bottom:8px">Teal = recommended for your problem. Grey = available to add. Click + Add to manually include any capability.</p>', unsafe_allow_html=True)

    scores = st.session_state.scores
    manually_added = st.session_state.manually_added
    manually_removed = st.session_state.manually_removed

    for layer_id in get_layers_ordered():
        layer = LAYER_REGISTRY[layer_id]
        all_caps = get_caps_for_layer(layer_id)

        # Count recommended (excluding manually removed)
        n_recommended = sum(
            1 for c in all_caps
            if get_status(c["id"], scores.get(c["id"], 50), manually_added, manually_removed) in (STATUS_RECOMMENDED, STATUS_MANUALLY_ADDED)
        )

        render_layer_header(layer_id, layer, n_recommended, len(manually_added))

        # Filter: show recommended + available, hide not_recommended unless toggled
        show_all = st.session_state.show_not_recommended.get(layer_id, False)
        display_caps = [
            c for c in all_caps
            if get_status(c["id"], scores.get(c["id"], 50), manually_added, manually_removed) != STATUS_NOT_RECOMMENDED
            or show_all
        ] if True else all_caps

        # Sort: recommended first, then manually added, then available, then not recommended
        def sort_key(c):
            s = get_status(c["id"], scores.get(c["id"], 50), manually_added, manually_removed)
            order = {STATUS_RECOMMENDED: 0, STATUS_MANUALLY_ADDED: 1, STATUS_AVAILABLE: 2, STATUS_NOT_RECOMMENDED: 3, STATUS_MANUALLY_REMOVED: 4}
            return (order.get(s, 5), -scores.get(c["id"], 0))
        display_caps.sort(key=sort_key)

        # Render in rows of 5
        COLS = 5
        for i in range(0, len(display_caps), COLS):
            chunk = display_caps[i:i+COLS]
            cols = st.columns(COLS)
            for j, cap in enumerate(chunk):
                with cols[j]:
                    cap_id = cap["id"]
                    score = scores.get(cap_id, 50)
                    status = get_status(cap_id, score, manually_added, manually_removed)
                    render_capability_card(cap, score, status)

                    if status == STATUS_MANUALLY_REMOVED:
                        if st.button("↩ Restore", key=f"restore_{cap_id}", use_container_width=True):
                            st.session_state.manually_removed.discard(cap_id)
                            st.rerun()
                    elif status == STATUS_RECOMMENDED:
                        if st.button("− Remove", key=f"remove_{cap_id}", use_container_width=True):
                            st.session_state.manually_removed.add(cap_id)
                            st.rerun()
                    elif status == STATUS_MANUALLY_ADDED:
                        if st.button("− Remove", key=f"remove_added_{cap_id}", use_container_width=True):
                            st.session_state.manually_added.discard(cap_id)
                            st.rerun()
                    else:
                        if st.button("+ Add", key=f"add_{cap_id}", use_container_width=True):
                            st.session_state.interrogating = cap_id
                            st.session_state.interrog_answers = {}
                            st.rerun()

        # Toggle show not-recommended
        not_rec_count = sum(
            1 for c in all_caps
            if get_status(c["id"], scores.get(c["id"], 50), manually_added, manually_removed) == STATUS_NOT_RECOMMENDED
        )
        if not_rec_count > 0:
            label = f"Hide {not_rec_count} low-fit" if show_all else f"Show {not_rec_count} low-fit"
            if st.button(label, key=f"toggle_nr_{layer_id}"):
                st.session_state.show_not_recommended[layer_id] = not show_all
                st.rerun()

    # ─── Interrogation Panel ──────────────────────────────────────────────────
    if st.session_state.interrogating:
        cap_id = st.session_state.interrogating
        cap = CAPABILITY_REGISTRY.get(cap_id)
        if cap:
            st.divider()
            st.markdown(
                f'<div style="background:#FEF3C7;border:1px solid #FDE68A;border-radius:12px;padding:16px 20px;margin-bottom:12px">'
                f'<div style="font-size:13px;font-weight:800;color:#92400E;margin-bottom:4px">Validating: {cap["icon"]} {cap["name"]}</div>'
                f'<div style="font-size:12px;color:#78350F">Answer these questions to confirm this capability fits your use case.</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

            questions = cap.get("interrogation", [])
            answers = st.session_state.interrog_answers.copy()
            all_answered = True

            for i, q_data in enumerate(questions):
                q_text = q_data["q"]
                answer = answers.get(i)
                if answer is None:
                    all_answered = False
                c1, c2, c3 = st.columns([6, 1, 1])
                with c1:
                    st.markdown(f'<p style="font-size:13px;color:{TEXT};margin:8px 0 4px"><strong>Q{i+1}:</strong> {q_text}</p>', unsafe_allow_html=True)
                with c2:
                    if st.button("Yes", key=f"iq_yes_{cap_id}_{i}", type="primary" if answer == True else "secondary"):
                        st.session_state.interrog_answers[i] = True
                        st.rerun()
                with c3:
                    if st.button("No", key=f"iq_no_{cap_id}_{i}", type="primary" if answer == False else "secondary"):
                        st.session_state.interrog_answers[i] = False
                        st.rerun()

            if len(st.session_state.interrog_answers) == len(questions) and questions:
                verdict = evaluate_interrogation(cap_id, st.session_state.interrog_answers)
                v = verdict["verdict"]
                v_color = {"justified": "#059669", "maybe": "#D97706", "premature": "#DC2626"}.get(v, TEXT)
                v_bg = {"justified": "#D1FAE5", "maybe": "#FEF3C7", "premature": "#FEE2E2"}.get(v, "#F8FAFC")
                v_label = {"justified": "Justified", "maybe": "Proceed with Caution", "premature": "Premature"}.get(v, v)

                st.markdown(
                    f'<div style="background:{v_bg};border:1px solid {v_color};border-radius:10px;padding:14px 18px;margin:12px 0">'
                    f'<div style="font-size:13px;font-weight:800;color:{v_color};margin-bottom:4px">Verdict: {v_label}</div>'
                    f'<div style="font-size:13px;color:{TEXT}">{verdict["reasoning"]}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

                col_confirm, col_cancel, _ = st.columns([1, 1, 3])
                with col_confirm:
                    if st.button("✓ Confirm Add", key=f"confirm_{cap_id}", type="primary"):
                        st.session_state.manually_added.add(cap_id)
                        st.session_state.interrogating = None
                        st.session_state.interrog_answers = {}
                        st.rerun()
                with col_cancel:
                    if st.button("Cancel", key=f"cancel_{cap_id}"):
                        st.session_state.interrogating = None
                        st.session_state.interrog_answers = {}
                        st.rerun()

    # ─── Architecture Summary ─────────────────────────────────────────────────
    st.divider()
    render_architecture_summary(scores, manually_added, manually_removed, pattern, st.session_state.analysis)
