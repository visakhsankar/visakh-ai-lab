"""
UI components for the Agent Systems Playground.
All rendering uses the same light-theme palette as the other demos.
"""
import json
import time

import streamlit as st

from agent.multi_agent import AGENTS

# ── Palette ────────────────────────────────────────────────────────────────────
_BLUE   = "#3B82F6"
_GREEN  = "#22C55E"
_AMBER  = "#F59E0B"
_RED    = "#EF4444"
_PURPLE = "#7C3AED"
_TEXT   = "#1E293B"
_MUTED  = "#64748B"
_BORDER = "#E2E8F0"
_LIGHT  = "#F1F5F9"
_WHITE  = "#FFFFFF"

# Tool icon map
_TOOL_ICONS = {
    "web_search": "🔍",
    "calculator": "🧮",
    "remember":   "💾",
    "recall":     "🗃️",
    "summarise":  "📋",
}

# Step type config
_STEP_CFG = {
    "think":   {"icon": "🧠", "label": "THINKING",   "bg": "#EFF6FF", "border": _BLUE,   "text": "#1D4ED8"},
    "act":     {"icon": "🔧", "label": "TOOL CALL",   "bg": "#FEF3C7", "border": _AMBER,  "text": "#B45309"},
    "observe": {"icon": "👁️", "label": "RESULT",      "bg": "#F0FDF4", "border": _GREEN,  "text": "#15803D"},
    "done":    {"icon": "✅", "label": "FINAL ANSWER","bg": "#EFF6FF", "border": _BLUE,   "text": "#1D4ED8"},
    "error":   {"icon": "⚠️", "label": "ERROR",       "bg": "#FEF2F2", "border": _RED,    "text": "#B91C1C"},
    "delegate":{"icon": "→",  "label": "DELEGATING",  "bg": "#FAF5FF", "border": _PURPLE, "text": "#6D28D9"},
    "plan":    {"icon": "📋", "label": "PLAN",        "bg": "#EFF6FF", "border": _BLUE,   "text": "#1D4ED8"},
    "orchestrator_done": {"icon": "🎯", "label": "COMPLETE", "bg": "#F0FDF4", "border": _GREEN, "text": "#15803D"},
}


# ── Agent badge ────────────────────────────────────────────────────────────────

def _agent_badge(agent_key: str) -> str:
    a = AGENTS.get(agent_key, {"name": agent_key.title(), "emoji": "🤖", "color": _MUTED, "bg": _LIGHT})
    return (
        f'<span style="background:{a["bg"]};color:{a["color"]};border:1px solid {a["color"]}44;'
        f'border-radius:20px;padding:2px 10px;font-size:11px;font-weight:700;margin-right:8px;">'
        f'{a["emoji"]} {a["name"]}</span>'
    )


# ── Single step card ───────────────────────────────────────────────────────────

def render_step(step: dict, show_agent_badge: bool = False) -> None:
    """Render one agent step as a styled card."""
    stype  = step.get("type", "think")
    cfg    = _STEP_CFG.get(stype, _STEP_CFG["think"])
    ms     = step.get("time_ms", 0)
    timing = f'<span style="font-size:10px;color:{_MUTED};margin-left:8px;">{ms}ms</span>' if ms else ""
    badge  = _agent_badge(step["agent"]) if show_agent_badge else ""

    # Build body HTML based on step type
    if stype == "think":
        body = f'<div style="font-size:13.5px;color:{_TEXT};line-height:1.7;">{step.get("content","")}</div>'

    elif stype == "act":
        tool   = step.get("tool", "")
        icon   = _TOOL_ICONS.get(tool, "🔧")
        inputs = step.get("inputs", {})
        args_str = " · ".join(f'<b>{k}</b>: {str(v)[:120]}' for k, v in inputs.items())
        body = (
            f'<div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;">'
            f'<span style="background:{_AMBER}22;color:{_AMBER};border-radius:6px;padding:3px 10px;'
            f'font-size:12px;font-weight:700;">{icon} {tool}</span></div>'
            f'<div style="background:{_LIGHT};border-radius:6px;padding:8px 12px;'
            f'font-size:12px;color:{_MUTED};">{args_str}</div>'
        )

    elif stype == "observe":
        output = step.get("output", "")
        preview = output[:800] + ("…" if len(output) > 800 else "")
        preview_html = preview.replace("\n", "<br>")
        body = (
            f'<div style="background:#F8FAFC;border-radius:8px;padding:12px;'
            f'font-size:12.5px;color:{_TEXT};line-height:1.65;max-height:220px;overflow-y:auto;">'
            f'{preview_html}</div>'
        )

    elif stype == "done":
        content = step.get("content", "").replace("\n", "<br>")
        body = (
            f'<div style="font-size:14px;color:{_TEXT};line-height:1.8;font-family:Georgia,serif;">'
            f'{content}</div>'
        )

    elif stype == "plan":
        content = step.get("content", "")
        steps   = step.get("steps", [])
        steps_html = "".join(
            f'<div style="display:flex;align-items:center;gap:8px;padding:5px 0;">'
            f'<span style="color:{AGENTS.get(s["agent"],{}).get("color",_MUTED)};font-size:14px;">'
            f'{AGENTS.get(s["agent"],{}).get("emoji","🤖")}</span>'
            f'<span style="font-size:12px;color:{_TEXT};"><b>{s["agent"].title()}</b>: {s["subtask"][:100]}</span>'
            f'</div>'
            for s in steps
        )
        body = (
            f'<div style="font-size:13px;color:{_TEXT};margin-bottom:10px;font-style:italic;">{content}</div>'
            f'<div style="border-top:1px solid {_BORDER};padding-top:8px;">{steps_html}</div>'
        )

    elif stype == "delegate":
        target = step.get("target_agent", "")
        a      = AGENTS.get(target, {"name": target.title(), "emoji": "🤖", "color": _PURPLE, "bg": "#FAF5FF"})
        body = (
            f'<div style="display:flex;align-items:center;gap:10px;">'
            f'<span style="font-size:22px;">{a["emoji"]}</span>'
            f'<span style="font-size:13px;color:{_TEXT};">{step.get("content","")}</span>'
            f'</div>'
        )

    elif stype == "orchestrator_done":
        body = f'<div style="font-size:13px;color:{cfg["text"]};font-weight:600;">{step.get("content","")}</div>'

    else:
        body = f'<div style="font-size:13px;color:{_RED};">{step.get("content","")}</div>'

    st.markdown(
        f"""
        <div style="background:{cfg['bg']};border:1px solid {_BORDER};
                    border-left:4px solid {cfg['border']};border-radius:10px;
                    padding:14px 18px;margin-bottom:10px;
                    box-shadow:0 1px 4px rgba(0,0,0,0.04);">
          <div style="display:flex;align-items:center;margin-bottom:8px;">
            {badge}
            <span style="font-size:16px;margin-right:6px;">{cfg['icon']}</span>
            <span style="font-size:10px;font-weight:700;letter-spacing:1.5px;
                         color:{cfg['text']};text-transform:uppercase;">{cfg['label']}</span>
            {timing}
          </div>
          {body}
        </div>
        """,
        unsafe_allow_html=True,
    )


# ── Memory panel ───────────────────────────────────────────────────────────────

def render_memory_panel(short_term: dict, long_term: dict) -> None:
    """Show short-term and long-term memory side by side."""
    st.markdown(
        f'<h4 style="color:{_TEXT};margin-bottom:4px;">🧠 Agent Memory</h4>',
        unsafe_allow_html=True,
    )
    col_st, col_lt = st.columns(2)

    with col_st:
        st.markdown(
            f'<div style="font-size:11px;font-weight:700;color:{_MUTED};text-transform:uppercase;'
            f'letter-spacing:1px;margin-bottom:8px;">Short-term (this run)</div>',
            unsafe_allow_html=True,
        )
        if short_term:
            rows = "".join(
                f'<div style="border-bottom:1px solid {_BORDER};padding:6px 0;font-size:12px;">'
                f'<b style="color:{_BLUE};">{k}</b><br>'
                f'<span style="color:{_TEXT};">{v}</span></div>'
                for k, v in short_term.items()
            )
            st.markdown(
                f'<div style="background:#fff;border:1px solid {_BORDER};border-radius:8px;padding:10px 14px;">'
                f'{rows}</div>',
                unsafe_allow_html=True,
            )
        else:
            st.caption("Nothing stored yet.")

    with col_lt:
        st.markdown(
            f'<div style="font-size:11px;font-weight:700;color:{_MUTED};text-transform:uppercase;'
            f'letter-spacing:1px;margin-bottom:8px;">Long-term (across runs)</div>',
            unsafe_allow_html=True,
        )
        if long_term:
            rows = "".join(
                f'<div style="border-bottom:1px solid {_BORDER};padding:6px 0;font-size:12px;">'
                f'<b style="color:{_GREEN};">{k}</b>'
                f'<span style="color:{_MUTED};font-size:10px;margin-left:6px;">{v.get("stored_at","")}</span><br>'
                f'<span style="color:{_TEXT};">{v["value"]}</span></div>'
                for k, v in long_term.items()
            )
            st.markdown(
                f'<div style="background:#fff;border:1px solid {_BORDER};border-radius:8px;padding:10px 14px;">'
                f'{rows}</div>',
                unsafe_allow_html=True,
            )
            if st.button("🗑️ Clear long-term memory", key="clear_lt"):
                st.session_state["_agent_long_term_memory"] = {}
                st.rerun()
        else:
            st.caption("Nothing stored yet. The agent will save facts here using the 'remember' tool.")


# ── Analytics panel ────────────────────────────────────────────────────────────

def render_analytics(steps: list, elapsed_s: float) -> None:
    """Show post-run analytics metrics."""
    think_count   = sum(1 for s in steps if s["type"] == "think")
    tool_calls    = [s for s in steps if s["type"] == "act"]
    tool_count    = len(tool_calls)
    tools_used    = list(dict.fromkeys(s["tool"] for s in tool_calls))
    total_ms      = sum(s.get("time_ms", 0) for s in steps)

    st.markdown(
        f'<h4 style="color:{_TEXT};margin-bottom:4px;">📊 Run Analytics</h4>',
        unsafe_allow_html=True,
    )

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🔄 Total Steps",   len(steps))
    c2.metric("🔧 Tool Calls",    tool_count)
    c3.metric("🧠 Think Steps",   think_count)
    c4.metric("⏱️ Elapsed",       f"{elapsed_s:.1f}s")

    if tools_used:
        badges = " ".join(
            f'<span style="background:{_LIGHT};border:1px solid {_BORDER};border-radius:20px;'
            f'padding:3px 10px;font-size:12px;color:{_TEXT};margin:2px;">'
            f'{_TOOL_ICONS.get(t,"🔧")} {t}</span>'
            for t in tools_used
        )
        st.markdown(
            f'<div style="margin-top:8px;">'
            f'<span style="font-size:12px;color:{_MUTED};margin-right:8px;">Tools used:</span>'
            f'{badges}</div>',
            unsafe_allow_html=True,
        )


# ── Sidebar tool status ────────────────────────────────────────────────────────

def render_tool_status() -> None:
    """Show which tools are available in the sidebar."""
    import os
    has_openai = bool(os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY", ""))
    has_tavily = bool(os.getenv("TAVILY_API_KEY") or st.secrets.get("TAVILY_API_KEY", ""))

    tool_rows = [
        ("🔍 Web Search",  has_tavily,  "Tavily"),
        ("🧮 Calculator",  True,        "Built-in"),
        ("💾 Remember",    True,        "Session"),
        ("🗃️ Recall",      True,        "Session"),
        ("📋 Summarise",   has_openai,  "OpenAI"),
    ]
    st.markdown(
        f'<div style="font-size:11px;font-weight:700;color:{_MUTED};text-transform:uppercase;'
        f'letter-spacing:1px;margin-bottom:8px;">Available Tools</div>',
        unsafe_allow_html=True,
    )
    for name, available, source in tool_rows:
        dot   = f'<span style="color:{_GREEN};">●</span>' if available else f'<span style="color:{_RED};">●</span>'
        state = "Ready" if available else "Missing key"
        st.markdown(
            f'<div style="display:flex;justify-content:space-between;font-size:12px;'
            f'padding:4px 0;border-bottom:1px solid {_BORDER};">'
            f'<span>{dot} {name}</span>'
            f'<span style="color:{_MUTED};">{state}</span></div>',
            unsafe_allow_html=True,
        )
