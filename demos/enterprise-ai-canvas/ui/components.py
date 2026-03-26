"""UI components for Enterprise AI Canvas."""
from __future__ import annotations
import streamlit as st

TEAL = "#0F766E"
TEAL_LIGHT = "#F0FDFA"
TEAL_BORDER = "#99F6E4"
TEAL_SELECTED = "#CCFBF1"
TEXT = "#1e293b"
MUTED = "#64748b"
CARD_BG = "#ffffff"
CARD_BORDER = "#e2e8f0"
PAGE_BG = "#f8fafc"

SCORE_COLORS = {
    "high":   ("#059669", "#D1FAE5"),  # green
    "medium": ("#D97706", "#FEF3C7"),  # amber
    "low":    ("#DC2626", "#FEE2E2"),  # red
}

TRADE_OFF_COLORS = {
    "very_low": "#059669", "low": "#22C55E", "medium": "#D97706",
    "high": "#EF4444", "very_high": "#DC2626",
}


def render_header():
    st.markdown('<h1 style="font-size:2.2rem;font-weight:800;color:#1e293b;margin-bottom:2px">🏗️ Enterprise AI Canvas</h1>', unsafe_allow_html=True)
    st.markdown('<p style="font-size:16px;color:#64748b;margin-bottom:2px">Describe your problem. Get a full capability architecture — with reasoning.</p>', unsafe_allow_html=True)
    st.markdown('<p style="font-size:12px;color:#94a3b8;margin-bottom:0">by <a href="https://visakhsankar.com" style="color:#0F766E;text-decoration:none;font-weight:600">Visakh Sankar</a></p>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)


def render_signal_chips(signals: list[str]) -> None:
    chips = " ".join(
        f'<span style="display:inline-block;background:#E0F2FE;color:#0369A1;font-size:11px;font-weight:600;padding:3px 8px;border-radius:12px;margin:2px">{s.replace("_", " ")}</span>'
        for s in signals
    )
    st.markdown(f'<div style="line-height:2">{chips}</div>', unsafe_allow_html=True)


def render_analysis_summary(analysis: dict) -> None:
    st.markdown(
        f'<div style="background:linear-gradient(135deg,{TEAL_LIGHT},{TEAL_SELECTED});border:1px solid {TEAL_BORDER};border-radius:14px;padding:20px 24px;margin-bottom:16px">'
        f'<div style="font-size:11px;font-weight:800;color:{TEAL};text-transform:uppercase;letter-spacing:1px;margin-bottom:8px">Analysis Complete</div>'
        f'<div style="font-size:15px;font-weight:700;color:{TEXT};margin-bottom:4px">{analysis.get("industry", "")} — {analysis.get("use_case_summary", "")}</div>'
        f'<div style="font-size:13px;color:{MUTED};margin-bottom:12px">{analysis.get("reasoning", "")}</div>'
        f'<div style="font-size:11px;font-weight:700;color:{TEAL};text-transform:uppercase;letter-spacing:0.5px;margin-bottom:6px">Detected Signals</div>'
        f'</div>',
        unsafe_allow_html=True,
    )
    render_signal_chips(analysis.get("signals", []))


def render_constraint_card(cid: str, constraint: dict, active: bool) -> None:
    is_hard = constraint["type"] == "hard"
    type_color = "#DC2626" if is_hard else "#D97706"
    type_bg = "#FEE2E2" if is_hard else "#FEF3C7"
    type_label = "HARD" if is_hard else "SOFT"
    border = f"2px solid {TEAL}" if active else f"1px solid {CARD_BORDER}"
    bg = TEAL_LIGHT if active else CARD_BG
    st.markdown(
        f'<div style="background:{bg};border:{border};border-radius:10px;padding:12px 14px;margin:4px 0">'
        f'<div style="display:flex;align-items:center;gap:8px;margin-bottom:4px">'
        f'<span style="background:{type_bg};color:{type_color};font-size:9px;font-weight:800;padding:2px 6px;border-radius:4px">{type_label}</span>'
        f'<span style="font-size:12px;font-weight:700;color:{TEXT}">{constraint["label"]}</span>'
        f'</div>'
        f'<p style="font-size:11px;color:{MUTED};margin:0;line-height:1.4">{constraint["description"]}</p>'
        f'</div>',
        unsafe_allow_html=True,
    )


def render_capability_card(cap: dict, score: int, status: str) -> None:
    is_recommended = status == "recommended"
    is_manually_added = status == "manually_added"
    is_not_recommended = status == "not_recommended"
    is_removed = status == "manually_removed"

    if is_recommended:
        bg, border = TEAL_SELECTED, f"2px solid {TEAL}"
        badge_bg, badge_color = TEAL, "#ffffff"
        badge_text = "Recommended"
    elif is_manually_added:
        bg, border = "#FEF3C7", "2px solid #D97706"
        badge_bg, badge_color = "#D97706", "#ffffff"
        badge_text = "Added"
    elif is_not_recommended:
        bg, border = "#F8FAFC", "1px solid #CBD5E1"
        badge_bg, badge_color = "#94A3B8", "#ffffff"
        badge_text = "Low fit"
    else:
        bg, border = CARD_BG, f"1px solid {CARD_BORDER}"
        badge_bg, badge_color = "#64748B", "#ffffff"
        badge_text = "Available"

    to = cap.get("trade_offs", {})

    def to_dot(val):
        colors = {"very_low": "🟢", "low": "🟢", "medium": "🟡", "high": "🔴", "very_high": "🔴"}
        return colors.get(val, "⚪")

    score_pct = score
    score_color = "#059669" if score >= 65 else ("#D97706" if score >= 40 else "#DC2626")

    st.markdown(
        f'<div style="background:{bg};border:{border};border-radius:10px;padding:12px 14px;height:100%;min-height:160px">'
        f'<div style="display:flex;align-items:flex-start;justify-content:space-between;margin-bottom:6px">'
        f'<span style="font-size:20px">{cap.get("icon","🔧")}</span>'
        f'<span style="background:{badge_bg};color:{badge_color};font-size:9px;font-weight:700;padding:2px 6px;border-radius:4px">{badge_text}</span>'
        f'</div>'
        f'<div style="font-size:12px;font-weight:700;color:{TEXT};margin-bottom:2px">{cap["name"]}</div>'
        f'<div style="font-size:10px;color:{MUTED};margin-bottom:6px">{cap["vendor"]}</div>'
        f'<div style="font-size:11px;color:{MUTED};line-height:1.4;margin-bottom:8px">{cap["description"][:80]}{"..." if len(cap["description"]) > 80 else ""}</div>'
        f'<div style="display:flex;gap:6px;flex-wrap:wrap;margin-bottom:6px">'
        f'<span style="font-size:10px;color:{MUTED}">Cost:{to_dot(to.get("cost","medium"))}</span>'
        f'<span style="font-size:10px;color:{MUTED}">Quality:{to_dot(to.get("quality","medium"))}</span>'
        f'<span style="font-size:10px;color:{MUTED}">Latency:{to_dot(to.get("latency","medium"))}</span>'
        f'</div>'
        f'<div style="background:rgba(0,0,0,0.04);border-radius:4px;height:4px;margin-top:4px">'
        f'<div style="background:{score_color};height:4px;border-radius:4px;width:{score_pct}%"></div>'
        f'</div>'
        f'<div style="font-size:10px;color:{score_color};font-weight:700;margin-top:2px">Fit: {score_pct}%</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def render_layer_header(layer_id: str, layer: dict, n_recommended: int, n_selected: int) -> None:
    st.markdown(
        f'<div style="display:flex;align-items:center;gap:10px;margin:24px 0 8px">'
        f'<span style="font-size:20px">{layer["icon"]}</span>'
        f'<span style="font-size:14px;font-weight:800;color:{TEXT}">{layer["name"]}</span>'
        f'<span style="background:{TEAL_LIGHT};color:{TEAL};font-size:11px;font-weight:700;padding:2px 8px;border-radius:10px">{n_recommended} recommended</span>'
        f'<span style="font-size:11px;color:{MUTED}">{layer["description"]}</span>'
        f'</div>',
        unsafe_allow_html=True,
    )


def render_pattern_badge(pattern: str) -> None:
    st.markdown(
        f'<div style="display:inline-block;background:linear-gradient(135deg,{TEAL},{TEAL_BORDER});border-radius:20px;padding:6px 16px;margin:8px 0">'
        f'<span style="font-size:13px;font-weight:700;color:#ffffff">Detected Pattern: {pattern}</span>'
        f'</div>',
        unsafe_allow_html=True,
    )


def render_architecture_summary(scores: dict, manually_added: set, manually_removed: set, pattern: str, analysis: dict) -> None:
    from core.recommender import get_status, STATUS_RECOMMENDED, STATUS_MANUALLY_ADDED
    from core.capabilities import CAPABILITY_REGISTRY, LAYER_REGISTRY, get_layers_ordered

    selected = []
    for cap_id, score in scores.items():
        status = get_status(cap_id, score, manually_added, manually_removed)
        if status in (STATUS_RECOMMENDED, STATUS_MANUALLY_ADDED):
            selected.append(CAPABILITY_REGISTRY[cap_id])

    layers_covered = len(set(c["layer"] for c in selected))

    summary_lines = []
    for layer_id in get_layers_ordered():
        layer_caps = [c for c in selected if c["layer"] == layer_id]
        if layer_caps:
            names = ", ".join(c["name"] for c in layer_caps)
            summary_lines.append(f'<li style="margin-bottom:4px"><strong>{LAYER_REGISTRY[layer_id]["name"]}:</strong> {names}</li>')

    summary_html = "".join(summary_lines)

    st.markdown(
        f'<div style="background:#ffffff;border:1px solid {CARD_BORDER};border-radius:14px;padding:24px 28px;margin-top:16px">'
        f'<div style="font-size:11px;font-weight:800;color:{TEAL};text-transform:uppercase;letter-spacing:1px;margin-bottom:12px">Architecture Summary</div>'
        f'<div style="display:flex;gap:24px;margin-bottom:16px;flex-wrap:wrap">'
        f'<div style="text-align:center"><div style="font-size:28px;font-weight:800;color:{TEAL}">{len(selected)}</div><div style="font-size:11px;color:{MUTED};font-weight:600;text-transform:uppercase">Capabilities</div></div>'
        f'<div style="text-align:center"><div style="font-size:28px;font-weight:800;color:{TEAL}">{layers_covered}</div><div style="font-size:11px;color:{MUTED};font-weight:600;text-transform:uppercase">Layers</div></div>'
        f'<div style="text-align:center"><div style="font-size:28px;font-weight:800;color:{TEAL}">{len(manually_added)}</div><div style="font-size:11px;color:{MUTED};font-weight:600;text-transform:uppercase">Manually Added</div></div>'
        f'</div>'
        f'<ul style="font-size:13px;color:{TEXT};line-height:1.8;padding-left:18px;margin:0">{summary_html}</ul>'
        f'</div>',
        unsafe_allow_html=True,
    )
