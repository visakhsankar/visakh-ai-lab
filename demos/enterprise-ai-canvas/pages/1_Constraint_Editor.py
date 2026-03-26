"""Constraint Editor — explore all constraints and see their impact."""
from __future__ import annotations
import streamlit as st

TEAL = "#0F766E"
TEAL_LIGHT = "#F0FDFA"
TEAL_BORDER = "#99F6E4"
TEXT = "#1e293b"
MUTED = "#64748b"
CARD_BORDER = "#e2e8f0"

st.markdown("""
<style>
  .block-container { padding-top: 3rem; padding-bottom: 2rem; }
</style>
""", unsafe_allow_html=True)

from core.constraints import CONSTRAINT_REGISTRY
from core.capabilities import CAPABILITY_REGISTRY
from core.recommender import score_all, get_status, STATUS_RECOMMENDED

st.markdown(f'<h1 style="font-size:2.2rem;font-weight:800;color:#1e293b;margin-bottom:2px">⚙️ Constraint Editor</h1>', unsafe_allow_html=True)
st.markdown(f'<p style="font-size:16px;color:#64748b;margin-bottom:2px">Toggle constraints and see how the capability model shifts.</p>', unsafe_allow_html=True)
st.markdown(f'<p style="font-size:12px;color:#94a3b8">by <a href="https://visakhsankar.com" style="color:{TEAL};text-decoration:none;font-weight:600">Visakh Sankar</a></p>', unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

st.markdown(
    f'<div style="background:{TEAL_LIGHT};border:1px solid {TEAL_BORDER};border-radius:10px;padding:14px 18px;margin-bottom:20px">'
    f'<div style="font-size:13px;color:{TEXT};line-height:1.7">Toggle constraints below to explore how they affect the capability model. <strong>Hard constraints</strong> eliminate certain capabilities entirely. <strong>Soft constraints</strong> boost or penalise capability fit scores.</div>'
    f'</div>',
    unsafe_allow_html=True,
)

# ─── Constraint toggles ───────────────────────────────────────────────────────
if "editor_active_constraints" not in st.session_state:
    st.session_state.editor_active_constraints = set()

# Map constraint signals — we simulate signal sets from constraints
CONSTRAINT_TO_SIGNALS = {
    "gdpr_required":            ["gdpr", "data_residency", "high_data_sensitivity"],
    "hipaa_required":           ["hipaa", "high_data_sensitivity", "compliance_heavy"],
    "data_residency_required":  ["data_residency", "on_prem"],
    "audit_trail_required":     ["compliance_heavy"],
    "pii_handling_required":    ["high_data_sensitivity"],
    "no_external_apis":         ["on_prem", "vendor_lock_concern"],
    "on_prem_required":         ["on_prem"],
    "sub_second_latency":       ["ultra_low_latency", "realtime"],
    "high_availability":        ["high_volume", "external_users"],
    "streaming_output":         ["realtime", "external_users"],
    "cost_per_query_critical":  ["cost_critical"],
    "open_source_mandate":      ["open_source_preferred", "vendor_lock_concern"],
    "vendor_lock_avoidance":    ["vendor_lock_concern"],
    "azure_stack_standard":     ["existing_azure"],
    "time_to_market_critical":  ["low_team_maturity"],
    "team_maturity_low":        ["low_team_maturity"],
    "team_maturity_high":       ["high_team_maturity"],
    "multi_tenant_required":    ["multi_tenant"],
    "human_oversight_required": ["high_stakes_decisions"],
}

active = st.session_state.editor_active_constraints

for cat in ["Compliance", "Technical", "Business", "Operational"]:
    cat_cons = {cid: c for cid, c in CONSTRAINT_REGISTRY.items() if c["category"] == cat}
    if cat_cons:
        st.markdown(f'<div style="font-size:13px;font-weight:800;color:{TEXT};text-transform:uppercase;margin:20px 0 8px;padding-bottom:4px;border-bottom:2px solid {TEAL_BORDER}">{cat}</div>', unsafe_allow_html=True)
        for cid, c in cat_cons.items():
            is_hard = c["type"] == "hard"
            type_color = "#DC2626" if is_hard else "#D97706"
            type_label = "HARD" if is_hard else "SOFT"
            is_active = cid in active

            col1, col2 = st.columns([5, 1])
            with col1:
                st.markdown(
                    f'<div style="padding:10px 0">'
                    f'<div style="display:flex;align-items:center;gap:8px;margin-bottom:2px">'
                    f'<span style="background:{"#FEE2E2" if is_hard else "#FEF3C7"};color:{type_color};font-size:9px;font-weight:800;padding:2px 6px;border-radius:4px">{type_label}</span>'
                    f'<span style="font-size:13px;font-weight:600;color:{TEXT}">{c["label"]}</span>'
                    f'</div>'
                    f'<div style="font-size:12px;color:{MUTED}">{c["description"]}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
            with col2:
                toggled = st.toggle("", value=is_active, key=f"editor_toggle_{cid}", label_visibility="collapsed")
                if toggled != is_active:
                    if toggled:
                        st.session_state.editor_active_constraints.add(cid)
                    else:
                        st.session_state.editor_active_constraints.discard(cid)
                    st.rerun()

# ─── Impact view ─────────────────────────────────────────────────────────────
st.divider()
st.markdown(f'<div style="font-size:11px;font-weight:800;color:{TEAL};text-transform:uppercase;letter-spacing:1.5px;margin-bottom:12px">CAPABILITY IMPACT</div>', unsafe_allow_html=True)

if not active:
    st.info("Toggle some constraints above to see their impact on the capability model.")
else:
    # Derive signals from active constraints
    signals = []
    for cid in active:
        for sig in CONSTRAINT_TO_SIGNALS.get(cid, []):
            if sig not in signals:
                signals.append(sig)

    scores = score_all(signals)
    recommended = [(cap_id, s) for cap_id, s in sorted(scores.items(), key=lambda x: -x[1]) if s >= 65]
    not_recommended = [(cap_id, s) for cap_id, s in sorted(scores.items(), key=lambda x: x[1]) if s < 40]

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f'<div style="font-size:12px;font-weight:700;color:#059669;margin-bottom:8px">✅ Capabilities Boosted ({len(recommended)})</div>', unsafe_allow_html=True)
        for cap_id, score in recommended[:12]:
            cap = CAPABILITY_REGISTRY[cap_id]
            st.markdown(
                f'<div style="background:#D1FAE5;border:1px solid #6EE7B7;border-radius:6px;padding:6px 10px;margin:3px 0;display:flex;justify-content:space-between">'
                f'<span style="font-size:12px;color:#065F46;font-weight:600">{cap["icon"]} {cap["name"]}</span>'
                f'<span style="font-size:11px;color:#059669;font-weight:700">{score}%</span>'
                f'</div>',
                unsafe_allow_html=True,
            )

    with col2:
        st.markdown(f'<div style="font-size:12px;font-weight:700;color:#DC2626;margin-bottom:8px">❌ Capabilities Penalised ({len(not_recommended)})</div>', unsafe_allow_html=True)
        for cap_id, score in not_recommended[:12]:
            cap = CAPABILITY_REGISTRY[cap_id]
            st.markdown(
                f'<div style="background:#FEE2E2;border:1px solid #FECACA;border-radius:6px;padding:6px 10px;margin:3px 0;display:flex;justify-content:space-between">'
                f'<span style="font-size:12px;color:#991B1B;font-weight:600">{cap["icon"]} {cap["name"]}</span>'
                f'<span style="font-size:11px;color:#DC2626;font-weight:700">{score}%</span>'
                f'</div>',
                unsafe_allow_html=True,
            )
