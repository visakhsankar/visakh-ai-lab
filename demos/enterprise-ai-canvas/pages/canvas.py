"""Enterprise AI Canvas — main capability canvas page."""
from __future__ import annotations
import os
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

from core.capabilities import CAPABILITY_REGISTRY, LAYER_REGISTRY, get_layers_ordered, get_caps_for_layer
from core.constraints import CONSTRAINT_REGISTRY, signals_to_constraints
from core.analyzer import analyze_problem
from core.recommender import (
    score_all, get_status, detect_pattern, evaluate_interrogation,
    STATUS_RECOMMENDED, STATUS_AVAILABLE, STATUS_NOT_RECOMMENDED,
    STATUS_MANUALLY_ADDED, STATUS_MANUALLY_REMOVED,
)
from ui.components import (
    render_header, render_analysis_summary, render_capability_card,
    render_pattern_badge, render_architecture_summary, render_signal_chips,
)

TEAL = "#0F766E"
TEAL_LIGHT = "#F0FDFA"
TEAL_BORDER = "#99F6E4"
TEAL_SELECTED = "#CCFBF1"
TEXT = "#1e293b"
MUTED = "#64748b"
CARD_BORDER = "#e2e8f0"
MAX_ANALYSES = 5

st.markdown("""
<style>
  .block-container { padding-top: 3rem; padding-bottom: 2rem; }
  .stTextArea textarea { font-size: 14px; }
  .stExpander { border: 1px solid #e2e8f0 !important; border-radius: 10px !important; margin-bottom: 6px !important; }
</style>
""", unsafe_allow_html=True)

# ─── Session State ─────────────────────────────────────────────────────────────
defaults = {
    "analysis": None, "signals": [], "active_constraints": set(),
    "scores": {}, "manually_added": set(), "manually_removed": set(),
    "interrogating": None, "interrog_answers": {},
    "show_not_recommended": {}, "analysis_count": 0, "author_mode": False,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ─── API Key ───────────────────────────────────────────────────────────────────
openai_key = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY", "")
if not openai_key:
    st.error("⚠️ **OPENAI_API_KEY** missing. Add it to .env and restart.")
    st.stop()
openai_client = OpenAI(api_key=openai_key)

# ─── Sidebar — clean, just run counter + author access ────────────────────────
with st.sidebar:
    st.markdown("## 🏗️ AI Canvas")
    st.divider()

    runs_left = MAX_ANALYSES - st.session_state.analysis_count
    runs_display = "∞" if st.session_state.author_mode else str(max(runs_left, 0))
    limit_label = "∞" if st.session_state.author_mode else str(MAX_ANALYSES)
    st.markdown(
        f'<div style="text-align:center;padding:10px;background:{TEAL_LIGHT};border:1px solid {TEAL_BORDER};border-radius:8px"><span style="font-size:22px;font-weight:800;color:{TEAL}">{runs_display}</span><span style="font-size:12px;color:{TEAL};font-weight:600"> / {limit_label} analyses</span></div>',
        unsafe_allow_html=True,
    )

    if st.session_state.analysis:
        st.divider()
        st.markdown(f'<div style="font-size:11px;font-weight:700;color:{MUTED};text-transform:uppercase;letter-spacing:0.5px;margin-bottom:8px">Active Constraints</div>', unsafe_allow_html=True)
        active = st.session_state.active_constraints
        if active:
            for cid in sorted(active):
                c = CONSTRAINT_REGISTRY.get(cid)
                if c:
                    dot = "🔴" if c["type"] == "hard" else "🟡"
                    st.markdown(f'<div style="font-size:11px;color:{TEXT};padding:3px 0;line-height:1.4">{dot} {c["label"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<p style="font-size:12px;color:{MUTED}">None detected.</p>', unsafe_allow_html=True)

        pattern = detect_pattern(st.session_state.scores, st.session_state.manually_added, st.session_state.manually_removed)
        st.divider()
        st.markdown(f'<div style="font-size:11px;font-weight:700;color:{MUTED};text-transform:uppercase;letter-spacing:0.5px;margin-bottom:6px">Pattern</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="background:{TEAL_LIGHT};border:1px solid {TEAL_BORDER};border-radius:8px;padding:8px 12px;font-size:12px;font-weight:700;color:{TEAL}">{pattern}</div>', unsafe_allow_html=True)

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

# ─── Problem Input ─────────────────────────────────────────────────────────────
st.markdown(f'<div style="font-size:11px;font-weight:800;color:{TEAL};text-transform:uppercase;letter-spacing:1.5px;margin-bottom:8px">YOUR PROBLEM STATEMENT</div>', unsafe_allow_html=True)

EXAMPLES = [
    "A global bank wants to automate Tier 1 customer support across 12 markets. Must comply with GDPR and MAS regulations. Data cannot leave the EU or APAC regions.",
    "A healthcare startup is building an AI assistant for doctors to query patient records and clinical guidelines. HIPAA compliance required.",
    "An e-commerce company wants to build a product recommendation and search system for 10 million users. Must handle 50K queries per second at peak.",
    "A law firm wants to build an internal knowledge base assistant to search 20 years of case files, contracts, and legal precedents.",
    "A SaaS company is building an AI coding assistant as a product feature, to be exposed as an API to their developer customers.",
]
with st.expander("💡 Example problems"):
    for ex in EXAMPLES:
        st.markdown(f"• {ex}")

problem_input = st.text_area(
    "Problem", placeholder="Describe the business problem, industry, scale, compliance requirements, users, and constraints...",
    height=120, label_visibility="collapsed", key="problem_input",
)
col_l, col_c, col_r = st.columns([2, 1, 2])
with col_c:
    analyse_btn = st.button("🔍 Analyse & Build", use_container_width=True, type="primary")

# ─── Analysis Logic ────────────────────────────────────────────────────────────
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
    st.session_state.analysis = analysis
    st.session_state.signals = signals
    st.session_state.active_constraints = set(signals_to_constraints(signals))
    st.session_state.scores = score_all(signals)
    st.rerun()

# ─── Post-Analysis View ────────────────────────────────────────────────────────
if not st.session_state.analysis:
    st.stop()

render_analysis_summary(st.session_state.analysis)

pattern = detect_pattern(st.session_state.scores, st.session_state.manually_added, st.session_state.manually_removed)
render_pattern_badge(pattern)

st.markdown("<br>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 1 — CONSTRAINTS (inline, compact, grouped)
# ══════════════════════════════════════════════════════════════════════════════

active_constraints = st.session_state.active_constraints
n_active = len(active_constraints)
n_hard = sum(1 for cid in active_constraints if CONSTRAINT_REGISTRY.get(cid, {}).get("type") == "hard")
n_soft = n_active - n_hard

# Build constraint summary pills for the collapsed header
pill_html = ""
for cid in sorted(active_constraints)[:6]:
    c = CONSTRAINT_REGISTRY.get(cid)
    if c:
        is_hard = c["type"] == "hard"
        bg = "#FEE2E2" if is_hard else "#FEF3C7"
        color = "#DC2626" if is_hard else "#B45309"
        label = c["label"][:28] + ("…" if len(c["label"]) > 28 else "")
        pill_html += f'<span style="display:inline-block;background:{bg};color:{color};font-size:10px;font-weight:600;padding:2px 8px;border-radius:10px;margin:2px">{label}</span>'
if len(active_constraints) > 6:
    pill_html += f'<span style="display:inline-block;background:#F1F5F9;color:{MUTED};font-size:10px;font-weight:600;padding:2px 8px;border-radius:10px;margin:2px">+{len(active_constraints)-6} more</span>'

st.markdown(
    f'<div style="margin-bottom:4px"><span style="font-size:11px;font-weight:800;color:{TEAL};text-transform:uppercase;letter-spacing:1.5px">Constraints</span><span style="font-size:11px;color:{MUTED};margin-left:10px">{n_hard} hard · {n_soft} soft · {n_active} total active</span></div>',
    unsafe_allow_html=True,
)
if pill_html:
    st.markdown(f'<div style="margin-bottom:6px;line-height:2">{pill_html}</div>', unsafe_allow_html=True)

with st.expander("⚙️ Edit constraints — toggle to change the capability model", expanded=False):
    st.markdown(
        f'<div style="background:{TEAL_LIGHT};border:1px solid {TEAL_BORDER};border-radius:8px;padding:10px 14px;margin-bottom:14px;font-size:12px;color:{TEXT}">Turning a constraint <strong>on</strong> or <strong>off</strong> immediately rescores all 48 capabilities. Hard constraints eliminate incompatible options entirely.</div>',
        unsafe_allow_html=True,
    )
    constraint_changed = False
    for cat in ["Compliance", "Technical", "Business", "Operational"]:
        cat_items = {cid: c for cid, c in CONSTRAINT_REGISTRY.items() if c["category"] == cat}
        if not cat_items:
            continue
        active_in_cat = sum(1 for cid in cat_items if cid in active_constraints)

        # Category header with active count badge
        st.markdown(
            f'<div style="display:flex;align-items:center;gap:8px;margin:16px 0 8px;padding-bottom:6px;border-bottom:2px solid {TEAL_BORDER}">'
            f'<span style="font-size:12px;font-weight:800;color:{TEXT};text-transform:uppercase;letter-spacing:0.5px">{cat}</span>'
            f'<span style="background:{TEAL_LIGHT};color:{TEAL};font-size:10px;font-weight:700;padding:2px 7px;border-radius:8px">{active_in_cat} active</span>'
            f'</div>',
            unsafe_allow_html=True,
        )

        for cid, c in cat_items.items():
            is_hard = c["type"] == "hard"
            is_active = cid in active_constraints
            type_color = "#DC2626" if is_hard else "#D97706"
            type_bg = "#FEE2E2" if is_hard else "#FEF3C7"
            type_label = "HARD" if is_hard else "SOFT"
            row_bg = TEAL_LIGHT if is_active else "#ffffff"
            row_border = f"1px solid {TEAL_BORDER}" if is_active else f"1px solid {CARD_BORDER}"

            col_info, col_toggle = st.columns([5, 1])
            with col_info:
                st.markdown(
                    f'<div style="background:{row_bg};border:{row_border};border-radius:8px;padding:8px 12px;margin-bottom:2px">'
                    f'<div style="display:flex;align-items:center;gap:6px;margin-bottom:2px">'
                    f'<span style="background:{type_bg};color:{type_color};font-size:9px;font-weight:800;padding:2px 5px;border-radius:3px">{type_label}</span>'
                    f'<span style="font-size:12px;font-weight:600;color:{TEXT}">{c["label"]}</span>'
                    f'</div>'
                    f'<div style="font-size:11px;color:{MUTED};line-height:1.4">{c["description"]}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
            with col_toggle:
                st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
                toggled = st.toggle("", value=is_active, key=f"ctoggle_{cid}", label_visibility="collapsed")
                if toggled != is_active:
                    if toggled:
                        st.session_state.active_constraints.add(cid)
                    else:
                        st.session_state.active_constraints.discard(cid)
                    constraint_changed = True

    if constraint_changed:
        st.session_state.scores = score_all(st.session_state.signals)
        st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 2 — CAPABILITY CANVAS (layers as collapsible expanders)
# ══════════════════════════════════════════════════════════════════════════════

scores = st.session_state.scores
manually_added = st.session_state.manually_added
manually_removed = st.session_state.manually_removed

st.markdown(
    f'<div style="font-size:11px;font-weight:800;color:{TEAL};text-transform:uppercase;letter-spacing:1.5px;margin-bottom:4px">CAPABILITY CANVAS</div>'
    f'<p style="font-size:13px;color:{MUTED};margin-bottom:12px">Expand any layer to explore capabilities. Teal = recommended · Grey = available · Click + Add on any available capability.</p>',
    unsafe_allow_html=True,
)

for layer_id in get_layers_ordered():
    layer = LAYER_REGISTRY[layer_id]
    all_caps = get_caps_for_layer(layer_id)

    # Counts for header
    statuses = {c["id"]: get_status(c["id"], scores.get(c["id"], 50), manually_added, manually_removed) for c in all_caps}
    n_recommended = sum(1 for s in statuses.values() if s == STATUS_RECOMMENDED)
    n_added = sum(1 for s in statuses.values() if s == STATUS_MANUALLY_ADDED)
    n_available = sum(1 for s in statuses.values() if s == STATUS_AVAILABLE)
    n_selected = n_recommended + n_added

    # Build mini chip row for the expander label context
    rec_names = [c["name"] for c in all_caps if statuses[c["id"]] in (STATUS_RECOMMENDED, STATUS_MANUALLY_ADDED)]
    rec_preview = ", ".join(rec_names[:3]) + (f" +{len(rec_names)-3} more" if len(rec_names) > 3 else "")

    expander_label = f"{layer['icon']} {layer['name']} — {n_selected} selected"
    if n_available > 0:
        expander_label += f" · {n_available} available"
    if rec_preview:
        expander_label += f"  |  {rec_preview}"

    with st.expander(expander_label, expanded=False):

        # Layer description
        st.markdown(
            f'<div style="font-size:12px;color:{MUTED};margin-bottom:12px;padding-bottom:10px;border-bottom:1px solid {CARD_BORDER}">{layer["description"]}</div>',
            unsafe_allow_html=True,
        )

        show_all = st.session_state.show_not_recommended.get(layer_id, False)

        # Sort and filter
        def sort_key(c):
            s = statuses[c["id"]]
            order = {STATUS_RECOMMENDED: 0, STATUS_MANUALLY_ADDED: 1, STATUS_AVAILABLE: 2, STATUS_NOT_RECOMMENDED: 3, STATUS_MANUALLY_REMOVED: 4}
            return (order.get(s, 5), -scores.get(c["id"], 0))

        display_caps = sorted(
            [c for c in all_caps if statuses[c["id"]] != STATUS_NOT_RECOMMENDED or show_all],
            key=sort_key,
        )

        # Render in rows of 4 (better balance than 5)
        COLS = 4
        for i in range(0, len(display_caps), COLS):
            chunk = display_caps[i:i + COLS]
            cols = st.columns(COLS)
            for j, cap in enumerate(chunk):
                with cols[j]:
                    cap_id = cap["id"]
                    score = scores.get(cap_id, 50)
                    status = statuses[cap_id]
                    render_capability_card(cap, score, status)
                    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

                    if status == STATUS_MANUALLY_REMOVED:
                        if st.button("↩ Restore", key=f"restore_{cap_id}", use_container_width=True):
                            st.session_state.manually_removed.discard(cap_id)
                            st.rerun()
                    elif status in (STATUS_RECOMMENDED, STATUS_MANUALLY_ADDED):
                        if st.button("− Remove", key=f"rm_{cap_id}", use_container_width=True):
                            if status == STATUS_RECOMMENDED:
                                st.session_state.manually_removed.add(cap_id)
                            else:
                                st.session_state.manually_added.discard(cap_id)
                            st.rerun()
                    else:
                        if st.button("+ Add", key=f"add_{cap_id}", use_container_width=True):
                            st.session_state.interrogating = cap_id
                            st.session_state.interrog_answers = {}
                            st.rerun()

        # Low-fit toggle
        not_rec_count = sum(1 for c in all_caps if statuses[c["id"]] == STATUS_NOT_RECOMMENDED)
        if not_rec_count > 0:
            st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
            label = f"Hide {not_rec_count} low-fit capabilities" if show_all else f"Show {not_rec_count} low-fit capabilities"
            if st.button(label, key=f"toggle_nr_{layer_id}"):
                st.session_state.show_not_recommended[layer_id] = not show_all
                st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 3 — INTERROGATION PANEL (appears when + Add clicked)
# ══════════════════════════════════════════════════════════════════════════════

if st.session_state.interrogating:
    cap_id = st.session_state.interrogating
    cap = CAPABILITY_REGISTRY.get(cap_id)
    if cap:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            f'<div style="background:#FEF3C7;border:2px solid #FDE68A;border-radius:12px;padding:16px 20px;margin-bottom:12px">'
            f'<div style="font-size:14px;font-weight:800;color:#92400E;margin-bottom:2px">Validating: {cap["icon"]} {cap["name"]}</div>'
            f'<div style="font-size:12px;color:#78350F">Answer these 3 questions — we\'ll tell you if this is the right fit right now.</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

        for i, q_data in enumerate(cap.get("interrogation", [])):
            answer = st.session_state.interrog_answers.get(i)
            answered_yes = answer is True
            answered_no = answer is False
            q_bg = "#F0FDF4" if answered_yes else ("#FEF2F2" if answered_no else "#F8FAFC")
            q_border = "#BBF7D0" if answered_yes else ("#FECACA" if answered_no else CARD_BORDER)

            st.markdown(
                f'<div style="background:{q_bg};border:1px solid {q_border};border-radius:8px;padding:12px 14px;margin-bottom:4px">'
                f'<span style="font-size:13px;color:{TEXT}"><strong>Q{i+1}:</strong> {q_data["q"]}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )
            c1, c2, c3 = st.columns([4, 1, 1])
            with c2:
                if st.button("Yes", key=f"iq_yes_{cap_id}_{i}", type="primary" if answered_yes else "secondary", use_container_width=True):
                    st.session_state.interrog_answers[i] = True
                    st.rerun()
            with c3:
                if st.button("No", key=f"iq_no_{cap_id}_{i}", type="primary" if answered_no else "secondary", use_container_width=True):
                    st.session_state.interrog_answers[i] = False
                    st.rerun()

        if len(st.session_state.interrog_answers) == len(cap.get("interrogation", [])) and cap.get("interrogation"):
            verdict = evaluate_interrogation(cap_id, st.session_state.interrog_answers)
            v = verdict["verdict"]
            v_color = {"justified": "#059669", "maybe": "#D97706", "premature": "#DC2626"}.get(v, TEXT)
            v_bg = {"justified": "#D1FAE5", "maybe": "#FEF3C7", "premature": "#FEE2E2"}.get(v, "#F8FAFC")
            v_border = {"justified": "#6EE7B7", "maybe": "#FDE68A", "premature": "#FECACA"}.get(v, CARD_BORDER)
            v_label = {"justified": "✓ Justified", "maybe": "⚠ Proceed with Caution", "premature": "✗ Premature"}.get(v, v)
            st.markdown(
                f'<div style="background:{v_bg};border:2px solid {v_border};border-radius:10px;padding:14px 18px;margin:12px 0">'
                f'<div style="font-size:14px;font-weight:800;color:{v_color};margin-bottom:6px">Verdict: {v_label}</div>'
                f'<div style="font-size:13px;color:{TEXT};line-height:1.6">{verdict["reasoning"]}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
            col_confirm, col_cancel, _ = st.columns([1, 1, 3])
            with col_confirm:
                if st.button("✓ Confirm Add", key=f"confirm_{cap_id}", type="primary", use_container_width=True):
                    st.session_state.manually_added.add(cap_id)
                    st.session_state.interrogating = None
                    st.session_state.interrog_answers = {}
                    st.rerun()
            with col_cancel:
                if st.button("Cancel", key=f"cancel_{cap_id}", use_container_width=True):
                    st.session_state.interrogating = None
                    st.session_state.interrog_answers = {}
                    st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 4 — ARCHITECTURE SUMMARY
# ══════════════════════════════════════════════════════════════════════════════

st.markdown("<br>", unsafe_allow_html=True)
st.divider()
render_architecture_summary(scores, manually_added, manually_removed, pattern, st.session_state.analysis)
