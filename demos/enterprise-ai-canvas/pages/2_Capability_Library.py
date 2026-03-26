"""Capability Library — browse all 45 capability building blocks."""
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

from core.capabilities import CAPABILITY_REGISTRY, LAYER_REGISTRY, get_layers_ordered, get_caps_for_layer

st.markdown(f'<h1 style="font-size:2.2rem;font-weight:800;color:#1e293b;margin-bottom:2px">📦 Capability Library</h1>', unsafe_allow_html=True)
st.markdown(f'<p style="font-size:16px;color:#64748b;margin-bottom:2px">Every AI building block in the canvas — with trade-offs and interrogation questions.</p>', unsafe_allow_html=True)
st.markdown(f'<p style="font-size:12px;color:#94a3b8">by <a href="https://visakhsankar.com" style="color:{TEAL};text-decoration:none;font-weight:600">Visakh Sankar</a></p>', unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# Filters
col_search, col_layer = st.columns([3, 2])
with col_search:
    search = st.text_input("Search capabilities", placeholder="e.g. vector, RAG, fine-tune...", label_visibility="collapsed")
with col_layer:
    layer_options = ["All Layers"] + [LAYER_REGISTRY[lid]["name"] for lid in get_layers_ordered()]
    selected_layer = st.selectbox("Layer", layer_options, label_visibility="collapsed")

selected_layer_id = None
if selected_layer != "All Layers":
    selected_layer_id = next((lid for lid in LAYER_REGISTRY if LAYER_REGISTRY[lid]["name"] == selected_layer), None)

TRADE_OFF_LABELS = {"very_low": "Very Low", "low": "Low", "medium": "Medium", "high": "High", "very_high": "Very High"}
TRADE_OFF_COLORS = {"very_low": "#059669", "low": "#22C55E", "medium": "#D97706", "high": "#EF4444", "very_high": "#DC2626"}

for layer_id in get_layers_ordered():
    if selected_layer_id and layer_id != selected_layer_id:
        continue
    layer = LAYER_REGISTRY[layer_id]
    caps = get_caps_for_layer(layer_id)

    if search:
        caps = [c for c in caps if search.lower() in c["name"].lower() or search.lower() in c["description"].lower()]

    if not caps:
        continue

    st.markdown(
        f'<div style="display:flex;align-items:center;gap:10px;margin:28px 0 12px;padding-bottom:8px;border-bottom:2px solid {TEAL_BORDER}">'
        f'<span style="font-size:20px">{layer["icon"]}</span>'
        f'<span style="font-size:15px;font-weight:800;color:{TEXT}">{layer["name"]}</span>'
        f'<span style="font-size:12px;color:{MUTED}">{len(caps)} capabilities</span>'
        f'</div>',
        unsafe_allow_html=True,
    )

    for cap in caps:
        to = cap.get("trade_offs", {})
        with st.expander(f'{cap["icon"]} **{cap["name"]}** — {cap["vendor"]}', expanded=False):
            st.markdown(f'<p style="font-size:14px;color:{TEXT};line-height:1.7;margin-bottom:12px">{cap["description"]}</p>', unsafe_allow_html=True)

            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f'<div style="font-size:11px;font-weight:700;color:{MUTED};text-transform:uppercase;margin-bottom:6px">Trade-offs</div>', unsafe_allow_html=True)
                for metric, val in to.items():
                    color = TRADE_OFF_COLORS.get(val, MUTED)
                    label = TRADE_OFF_LABELS.get(val, val)
                    st.markdown(
                        f'<div style="display:flex;justify-content:space-between;padding:4px 0;border-bottom:1px solid #F1F5F9">'
                        f'<span style="font-size:12px;color:{TEXT};text-transform:capitalize">{metric.replace("_"," ")}</span>'
                        f'<span style="font-size:12px;font-weight:700;color:{color}">{label}</span>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )

            with col2:
                if cap.get("fit_signals"):
                    st.markdown(f'<div style="font-size:11px;font-weight:700;color:{MUTED};text-transform:uppercase;margin-bottom:6px">Best fit when...</div>', unsafe_allow_html=True)
                    for sig in cap["fit_signals"][:5]:
                        st.markdown(f'<div style="font-size:12px;color:#059669;padding:2px 0">✓ {sig.replace("_"," ")}</div>', unsafe_allow_html=True)
                if cap.get("contra_signals"):
                    st.markdown(f'<div style="font-size:11px;font-weight:700;color:{MUTED};text-transform:uppercase;margin:8px 0 4px">Avoid when...</div>', unsafe_allow_html=True)
                    for sig in cap["contra_signals"][:4]:
                        st.markdown(f'<div style="font-size:12px;color:#DC2626;padding:2px 0">✗ {sig.replace("_"," ")}</div>', unsafe_allow_html=True)

            if cap.get("dependencies"):
                deps = ", ".join(cap["dependencies"])
                st.markdown(f'<div style="font-size:12px;color:{MUTED};margin-top:8px">⚠️ Requires: {deps}</div>', unsafe_allow_html=True)

            if cap.get("interrogation"):
                st.markdown(f'<div style="font-size:11px;font-weight:700;color:{MUTED};text-transform:uppercase;margin:12px 0 6px">Validation Questions</div>', unsafe_allow_html=True)
                for i, q in enumerate(cap["interrogation"]):
                    good_label = "Yes" if q["good"] else "No"
                    st.markdown(
                        f'<div style="background:#F8FAFC;border:1px solid {CARD_BORDER};border-radius:6px;padding:8px 12px;margin-bottom:4px">'
                        f'<span style="font-size:12px;color:{TEXT}">Q{i+1}: {q["q"]}</span>'
                        f'<span style="font-size:11px;color:{TEAL};font-weight:700;margin-left:8px">(good answer: {good_label})</span>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )
