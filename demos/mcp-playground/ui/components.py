"""Visual components for MCP Playground."""
from __future__ import annotations

import json

import streamlit as st

# ─── Constants ────────────────────────────────────────────────────────────────

PURPLE = "#7C3AED"
PURPLE_LIGHT = "#EDE9FE"
PURPLE_BORDER = "#C4B5FD"
REQ_BG = "#EFF6FF"
REQ_BORDER = "#BFDBFE"
RESP_BG = "#F0FDF4"
RESP_BORDER = "#BBF7D0"
CARD_BG = "#ffffff"
CARD_BORDER = "#e2e8f0"
TEXT = "#1e293b"
MUTED = "#64748b"
PAGE_BG = "#f8fafc"

_ARCH_STAGES = [
    ("🤖", "Host"),
    ("📡", "Client"),
    ("⚙️", "Server"),
    ("🔧", "Tools"),
]

_STAGE_MAP = {
    "idle": -1,
    "handshake": 0,
    "discovery": 1,
    "calling": 2,
    "answering": 3,
}


# ─── Architecture Diagram ─────────────────────────────────────────────────────

def render_architecture_diagram(active_stage: str = "idle") -> None:
    """Render horizontal MCP architecture flow with active stage highlighted."""
    active_idx = _STAGE_MAP.get(active_stage, -1)

    nodes_html = ""
    for i, (icon, label) in enumerate(_ARCH_STAGES):
        is_active = (i == active_idx)
        if is_active:
            bg = PURPLE_LIGHT
            border = f"2px solid {PURPLE}"
            label_color = PURPLE
            icon_color = PURPLE
        else:
            bg = "#f1f5f9"
            border = "2px solid #e2e8f0"
            label_color = MUTED
            icon_color = "#94a3b8"

        nodes_html += (
            f'<div style="display:flex;flex-direction:column;align-items:center;gap:6px">'
            f'<div style="width:60px;height:60px;border-radius:14px;background:{bg};border:{border};'
            f'display:flex;align-items:center;justify-content:center;font-size:26px;'
            f'box-shadow:0 2px 8px rgba(0,0,0,0.06)">{icon}</div>'
            f'<span style="font-size:11px;font-weight:700;color:{label_color};text-transform:uppercase;letter-spacing:0.5px">{label}</span>'
            f'</div>'
        )

        if i < len(_ARCH_STAGES) - 1:
            arrow_color = PURPLE if (i < active_idx or active_idx == len(_ARCH_STAGES) - 1) else "#cbd5e1"
            nodes_html += (
                f'<div style="color:{arrow_color};font-size:24px;padding-bottom:18px;align-self:flex-start;padding-top:18px;font-weight:700">'
                f'&#8594;&#8594;</div>'
            )

    label_html = ""
    if active_stage != "idle":
        stage_labels = {
            "handshake": "Initialising MCP session...",
            "discovery": "Discovering available tools...",
            "calling": "Executing tool via MCP...",
            "answering": "Generating final answer...",
        }
        lbl = stage_labels.get(active_stage, "")
        label_html = (
            f'<div style="text-align:center;margin-top:8px;font-size:12px;'
            f'color:{PURPLE};font-weight:600;letter-spacing:0.3px">'
            f'&#9679; {lbl}</div>'
        )

    html = (
        f'<div style="background:linear-gradient(135deg,#f8fafc,#f1f5f9);'
        f'border:1px solid {CARD_BORDER};border-radius:14px;'
        f'padding:20px 32px;display:flex;flex-direction:column;align-items:center;gap:4px;margin:12px 0 4px">'
        f'<div style="display:flex;align-items:flex-start;justify-content:center;gap:8px;flex-wrap:wrap">'
        f'{nodes_html}'
        f'</div>'
        f'{label_html}'
        f'</div>'
    )
    st.markdown(html, unsafe_allow_html=True)


# ─── Protocol Message Card ────────────────────────────────────────────────────

def render_protocol_message(msg: dict) -> None:
    """Render a single JSON-RPC 2.0 message as a styled card."""
    direction = msg.get("direction", "request")
    method = msg.get("method", "")
    payload = msg.get("payload", {})
    duration_ms = msg.get("duration_ms")

    is_req = direction == "request"
    bg = REQ_BG if is_req else RESP_BG
    border_color = REQ_BORDER if is_req else RESP_BORDER
    badge_bg = "#3B82F6" if is_req else "#22C55E"
    badge_text = "&rarr; REQUEST" if is_req else "&larr; RESPONSE"

    payload_str = json.dumps(payload, indent=2)
    if len(payload_str) > 800:
        payload_str = payload_str[:800] + "\n  ... (truncated)"

    # escape for HTML
    payload_escaped = (
        payload_str
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )

    duration_html = ""
    if duration_ms is not None:
        duration_html = f'<span style="font-size:11px;color:{MUTED};margin-left:8px">{duration_ms}ms</span>'

    html = (
        f'<div style="background:{bg};border:1px solid {border_color};border-radius:10px;padding:14px 18px;margin:6px 0;font-family:inherit">'
        f'<div style="display:flex;align-items:center;gap:8px;margin-bottom:10px">'
        f'<span style="background:{badge_bg};color:#fff;font-size:10px;font-weight:700;padding:3px 8px;border-radius:4px;letter-spacing:0.5px">{badge_text}</span>'
        f'<span style="font-size:13px;font-weight:700;color:{TEXT};font-family:monospace">{method}</span>'
        f'{duration_html}'
        f'</div>'
        f'<pre style="background:rgba(255,255,255,0.7);border:1px solid {border_color};border-radius:6px;padding:10px 14px;margin:0;font-size:11px;color:#1e293b;overflow-x:auto;white-space:pre-wrap;word-break:break-all;line-height:1.5">{payload_escaped}</pre>'
        f'</div>'
    )
    st.markdown(html, unsafe_allow_html=True)


# ─── Tool Registry Sidebar ────────────────────────────────────────────────────

def render_tool_registry(tools: dict, call_counts: dict, active_tool: str = "") -> None:
    """Render tool cards in sidebar with call count badges."""
    for name, tool in tools.items():
        icon = tool.get("icon", "🔧")
        desc = tool.get("description", "")[:60]
        count = call_counts.get(name, 0)
        is_active = name == active_tool

        if is_active:
            border = f"2px solid {PURPLE}"
            bg = PURPLE_LIGHT
        else:
            border = f"1px solid {CARD_BORDER}"
            bg = "#ffffff"

        count_html = ""
        if count > 0:
            count_html = (
                f'<span style="background:{PURPLE};color:#fff;font-size:10px;font-weight:700;'
                f'padding:2px 6px;border-radius:10px;margin-left:4px">{count}</span>'
            )

        html = (
            f'<div style="background:{bg};border:{border};border-radius:8px;padding:8px 10px;margin:4px 0">'
            f'<div style="display:flex;align-items:center;gap:6px;margin-bottom:2px">'
            f'<span style="font-size:16px">{icon}</span>'
            f'<span style="font-size:12px;font-weight:700;color:{TEXT}">{name}</span>'
            f'{count_html}'
            f'</div>'
            f'<p style="font-size:11px;color:{MUTED};margin:0;line-height:1.4">{desc}</p>'
            f'</div>'
        )
        st.markdown(html, unsafe_allow_html=True)


# ─── Answer Card ─────────────────────────────────────────────────────────────

def render_answer_card(answer: str) -> None:
    """Render the final answer in a styled blue-gradient card."""
    answer_escaped = (
        answer
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace("\n", "<br>")
    )
    html = (
        f'<div style="background:linear-gradient(135deg,#EFF6FF,#F0F9FF);'
        f'border:1px solid #BFDBFE;border-radius:14px;padding:24px 28px;margin:16px 0">'
        f'<div style="font-size:12px;font-weight:700;color:#1D4ED8;text-transform:uppercase;letter-spacing:1px;margin-bottom:12px">Answer</div>'
        f'<div style="font-size:15px;color:{TEXT};line-height:1.7">{answer_escaped}</div>'
        f'</div>'
    )
    st.markdown(html, unsafe_allow_html=True)


# ─── Stats Row ────────────────────────────────────────────────────────────────

def render_stats_row(total_messages: int, tool_calls: int, total_time_ms: int) -> None:
    """Render a stats row showing protocol inspector summary."""
    html = (
        f'<div style="display:flex;gap:12px;margin:16px 0;flex-wrap:wrap">'
        f'<div style="background:#ffffff;border:1px solid {CARD_BORDER};border-radius:8px;padding:12px 18px;flex:1;min-width:100px;text-align:center">'
        f'<div style="font-size:22px;font-weight:800;color:{PURPLE}">{total_messages}</div>'
        f'<div style="font-size:11px;color:{MUTED};font-weight:600;text-transform:uppercase;letter-spacing:0.5px">Messages</div>'
        f'</div>'
        f'<div style="background:#ffffff;border:1px solid {CARD_BORDER};border-radius:8px;padding:12px 18px;flex:1;min-width:100px;text-align:center">'
        f'<div style="font-size:22px;font-weight:800;color:{PURPLE}">{tool_calls}</div>'
        f'<div style="font-size:11px;color:{MUTED};font-weight:600;text-transform:uppercase;letter-spacing:0.5px">Tool Calls</div>'
        f'</div>'
        f'<div style="background:#ffffff;border:1px solid {CARD_BORDER};border-radius:8px;padding:12px 18px;flex:1;min-width:100px;text-align:center">'
        f'<div style="font-size:22px;font-weight:800;color:{PURPLE}">{total_time_ms}ms</div>'
        f'<div style="font-size:11px;color:{MUTED};font-weight:600;text-transform:uppercase;letter-spacing:0.5px">Total Time</div>'
        f'</div>'
        f'</div>'
    )
    st.markdown(html, unsafe_allow_html=True)


# ─── Section Header ───────────────────────────────────────────────────────────

def render_section_label(text: str, subtitle: str = "") -> None:
    """Render an uppercase section label with optional subtitle."""
    sub_html = ""
    if subtitle:
        sub_html = f'<p style="font-size:13px;color:{MUTED};margin:4px 0 0">{subtitle}</p>'
    html = (
        f'<div style="margin:24px 0 12px">'
        f'<span style="font-size:11px;font-weight:800;color:{PURPLE};text-transform:uppercase;letter-spacing:1.5px">{text}</span>'
        f'{sub_html}'
        f'</div>'
    )
    st.markdown(html, unsafe_allow_html=True)
