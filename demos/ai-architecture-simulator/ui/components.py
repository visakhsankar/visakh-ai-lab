import streamlit as st
import plotly.graph_objects as go

# ── Shared palette (mirrors RAG Visual Simulator) ────────────────────────────
_GREEN  = "#22c55e"
_BLUE   = "#3b82f6"
_AMBER  = "#f59e0b"
_RED    = "#ef4444"
_PURPLE = "#a855f7"
_TEXT   = "#1e293b"
_MUTED  = "#64748b"
_LIGHT  = "#f1f5f9"
_BORDER = "#e2e8f0"


# ─── Constraint Tags ─────────────────────────────────────────────────────────

def render_constraint_tags(constraints: dict):
    """Render extracted constraints as colour-coded visual tags."""
    tag_defs = [
        ("latency_sensitivity", "⚡ Latency",     {"low": _GREEN,  "medium": _AMBER, "high": _RED}),
        ("budget",             "💰 Budget",       {"low": _RED,    "medium": _AMBER, "high": _GREEN}),
        ("data_sensitivity",   "🔒 Data Privacy", {"low": _GREEN,  "medium": _AMBER, "high": _RED}),
        ("team_capability",    "👥 Team Skill",   {"beginner": _RED, "intermediate": _AMBER,
                                                    "advanced": _BLUE, "expert": _GREEN}),
        ("scale",              "📈 Scale",        {"small": _BLUE, "medium": _AMBER,
                                                    "large": _PURPLE, "enterprise": _RED}),
    ]

    cols = st.columns(len(tag_defs))
    for col, (key, label, color_map) in zip(cols, tag_defs):
        value = constraints.get(key, "—")
        color = color_map.get(str(value).lower(), _MUTED)
        with col:
            st.markdown(
                f"""
                <div style="background:{color}18;border:1.5px solid {color};border-radius:10px;
                            padding:10px 8px;text-align:center;box-shadow:0 1px 3px rgba(0,0,0,0.06);">
                  <div style="font-size:11px;color:{_MUTED};margin-bottom:3px;">{label}</div>
                  <div style="font-weight:700;font-size:13px;text-transform:capitalize;color:{color};">{value}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


# ─── Radar Chart ─────────────────────────────────────────────────────────────

def render_radar_chart(patterns_data: list, pattern_names: list):
    """Return a Plotly radar figure comparing up to 3 patterns (light theme)."""
    categories = ["Accuracy", "Speed", "Privacy", "Cost Efficiency", "Scalability", "Simplicity"]
    score_keys = ["accuracy", "speed", "privacy", "cost_efficiency", "scalability", "simplicity"]
    line_colors = [_BLUE, _RED, _GREEN]
    fill_colors = ["rgba(59,130,246,0.12)", "rgba(239,68,68,0.12)", "rgba(34,197,94,0.12)"]

    fig = go.Figure()

    for i, (pattern, name) in enumerate(zip(patterns_data, pattern_names)):
        scores = [pattern["scores"].get(k, 0) for k in score_keys]
        scores_closed = scores + [scores[0]]
        cats_closed   = categories + [categories[0]]

        fig.add_trace(go.Scatterpolar(
            r=scores_closed,
            theta=cats_closed,
            fill="toself",
            name=name,
            line=dict(color=line_colors[i % len(line_colors)], width=2.5),
            fillcolor=fill_colors[i % len(fill_colors)],
        ))

    fig.update_layout(
        polar=dict(
            bgcolor="rgba(248,250,252,0.8)",
            radialaxis=dict(
                visible=True, range=[0, 5],
                tickfont=dict(size=9, color=_MUTED),
                gridcolor=_BORDER,
                linecolor=_BORDER,
            ),
            angularaxis=dict(
                tickfont=dict(size=12, color=_TEXT),
                linecolor=_BORDER,
            ),
        ),
        showlegend=True,
        legend=dict(
            font=dict(color=_TEXT, size=12),
            bgcolor="rgba(255,255,255,0.9)",
            bordercolor=_BORDER,
            borderwidth=1,
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=_TEXT),
        height=420,
        margin=dict(l=60, r=60, t=30, b=30),
    )
    return fig


# ─── Pattern Card ─────────────────────────────────────────────────────────────

def render_pattern_card(pattern: dict, recommendation: dict, rank: int = 1):
    """Render a recommendation card in the RAG-demo light style."""
    is_top      = rank == 1
    left_color  = _BLUE  if is_top else _BORDER
    badge_color = _BLUE  if is_top else _MUTED
    badge       = "🏆 RECOMMENDED" if is_top else f"#{rank} ALTERNATIVE"
    confidence  = recommendation.get("recommended", {}).get("confidence") if is_top else None

    conf_html = (
        f'<span style="background:{_BLUE}18;color:{_BLUE};border-radius:20px;'
        f'padding:2px 10px;font-size:13px;font-weight:700;">{confidence}% match</span>'
        if confidence else ""
    )

    components_html = "".join(
        f'<span style="background:{_LIGHT};border:1px solid {_BORDER};border-radius:5px;'
        f'padding:3px 8px;font-size:12px;color:{_MUTED};margin:2px;">{c}</span>'
        for c in pattern.get("key_components", [])
    )

    bg = "#eff6ff" if is_top else "#ffffff"

    st.markdown(
        f"""
        <div style="background:{bg};border:1px solid {_BORDER};border-left:4px solid {left_color};
                    border-radius:12px;padding:20px;margin-bottom:14px;
                    box-shadow:0 2px 6px rgba(0,0,0,0.05);">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
            <span style="color:{badge_color};font-size:11px;font-weight:700;letter-spacing:1.5px;">{badge}</span>
            {conf_html}
          </div>
          <h3 style="margin:0 0 2px 0;color:{_TEXT};font-size:19px;">{pattern["name"]}</h3>
          <p style="color:{_MUTED};margin:0 0 10px 0;font-size:13px;font-style:italic;">{pattern["tagline"]}</p>
          <p style="color:#374151;font-size:14px;line-height:1.65;margin-bottom:14px;">{pattern["description"]}</p>
          <div style="display:flex;gap:20px;margin-bottom:12px;flex-wrap:wrap;">
            <span style="font-size:13px;color:{_TEXT};">⏱️ <strong>{pattern["build_time"]}</strong></span>
            <span style="font-size:13px;color:{_TEXT};">👥 <strong>{pattern["team_needs"]}</strong></span>
          </div>
          <div style="margin-bottom:10px;display:flex;flex-wrap:wrap;gap:4px;">{components_html}</div>
          <div style="margin-top:8px;">
            <span style="font-size:12px;color:{_MUTED};text-transform:uppercase;letter-spacing:1px;">Stack: </span>
            <code style="background:{_LIGHT};padding:4px 10px;border-radius:4px;
                         font-size:12px;color:#1d4ed8;">{pattern["example_stack"]}</code>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ─── Why NOT Table ────────────────────────────────────────────────────────────

def render_why_not_table(rejected_patterns: list, all_patterns: list):
    """Render the 'Why NOT the others' table in light style."""
    pattern_map = {p["id"]: p for p in all_patterns}

    st.markdown("### ❌ Why NOT the Others")
    st.markdown(
        f'<p style="color:{_MUTED};font-size:13px;margin-bottom:16px;">'
        "Patterns explicitly considered and ruled out for your constraints.</p>",
        unsafe_allow_html=True,
    )

    rows_html = ""
    for item in rejected_patterns:
        p = pattern_map.get(item.get("pattern_id", ""))
        if p:
            rows_html += (
                f'<tr style="border-bottom:1px solid {_BORDER};">'
                f'<td style="padding:10px 14px;color:{_TEXT};font-weight:600;'
                f'white-space:nowrap;">{p["name"]}</td>'
                f'<td style="padding:10px 14px;color:{_RED};font-size:13px;">'
                f'{item["rejection_reason"]}</td>'
                f'</tr>'
            )

    st.markdown(
        f"""
        <table style="width:100%;border-collapse:collapse;border:1px solid {_BORDER};
                      border-radius:8px;overflow:hidden;background:#fff;">
          <thead>
            <tr style="background:{_LIGHT};">
              <th style="padding:10px 14px;text-align:left;color:{_MUTED};font-size:12px;
                         text-transform:uppercase;letter-spacing:1px;width:210px;">Pattern</th>
              <th style="padding:10px 14px;text-align:left;color:{_MUTED};font-size:12px;
                         text-transform:uppercase;letter-spacing:1px;">Reason Rejected</th>
            </tr>
          </thead>
          <tbody>{rows_html}</tbody>
        </table>
        """,
        unsafe_allow_html=True,
    )


# ─── Architecture Brief ───────────────────────────────────────────────────────

def render_architecture_brief(pattern: dict, constraints: dict, recommendation: dict):
    """Render the Architecture Brief in a blue-gradient card (mirrors RAG answer card)."""
    trade_offs_html = "".join(
        f'<li style="margin-bottom:6px;color:#1e3a5f;font-size:13px;">⚖️ {t}</li>'
        for t in recommendation.get("key_trade_offs", [])
    )
    watch_outs_html = "".join(
        f'<li style="margin-bottom:6px;color:#1e3a5f;font-size:13px;">⚠️ {w}</li>'
        for w in recommendation.get("implementation_watch_outs", [])
    )
    components_html = "".join(
        f'<li style="margin-bottom:4px;color:#1e3a5f;font-size:13px;">• {c}</li>'
        for c in pattern.get("key_components", [])
    )

    st.markdown(
        f"""
        <div style="background:linear-gradient(135deg,#eff6ff,#dbeafe);
                    border:1px solid #bfdbfe;border-radius:14px;padding:28px;">
          <div style="margin-bottom:20px;">
            <div style="font-size:13px;font-weight:700;color:#1d4ed8;
                        letter-spacing:0.05em;margin-bottom:4px;">📋 ARCHITECTURE BRIEF</div>
            <p style="color:{_MUTED};margin:0;font-size:13px;">
              Share this with your team or CTO as a starting point.
            </p>
          </div>
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-bottom:20px;">
            <div>
              <div style="color:{_MUTED};font-size:11px;text-transform:uppercase;
                          letter-spacing:1px;margin-bottom:5px;">Recommended Pattern</div>
              <div style="color:{_TEXT};font-size:17px;font-weight:700;">{pattern["name"]}</div>
            </div>
            <div>
              <div style="color:{_MUTED};font-size:11px;text-transform:uppercase;
                          letter-spacing:1px;margin-bottom:5px;">Use Case</div>
              <div style="color:{_TEXT};font-size:15px;">{constraints.get("use_case_type", "—")}</div>
            </div>
            <div>
              <div style="color:{_MUTED};font-size:11px;text-transform:uppercase;
                          letter-spacing:1px;margin-bottom:5px;">Build Timeline</div>
              <div style="color:#1d4ed8;font-size:15px;font-weight:700;">
                {recommendation.get("estimated_timeline", pattern["build_time"])}</div>
            </div>
            <div>
              <div style="color:{_MUTED};font-size:11px;text-transform:uppercase;
                          letter-spacing:1px;margin-bottom:5px;">Team Size</div>
              <div style="color:#1d4ed8;font-size:15px;font-weight:700;">
                {recommendation.get("estimated_team_size", pattern["team_needs"])}</div>
            </div>
            <div>
              <div style="color:{_MUTED};font-size:11px;text-transform:uppercase;
                          letter-spacing:1px;margin-bottom:5px;">Domain</div>
              <div style="color:{_TEXT};font-size:15px;text-transform:capitalize;">
                {constraints.get("domain", "—")}</div>
            </div>
            <div>
              <div style="color:{_MUTED};font-size:11px;text-transform:uppercase;
                          letter-spacing:1px;margin-bottom:5px;">Scale</div>
              <div style="color:{_TEXT};font-size:15px;text-transform:capitalize;">
                {constraints.get("scale", "—")}</div>
            </div>
          </div>
          <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:20px;">
            <div>
              <div style="color:{_MUTED};font-size:11px;text-transform:uppercase;
                          letter-spacing:1px;margin-bottom:8px;">Key Components</div>
              <ul style="margin:0;padding:0;list-style:none;">{components_html}</ul>
            </div>
            <div>
              <div style="color:{_MUTED};font-size:11px;text-transform:uppercase;
                          letter-spacing:1px;margin-bottom:8px;">Key Trade-offs</div>
              <ul style="margin:0;padding:0;list-style:none;">{trade_offs_html}</ul>
            </div>
            <div>
              <div style="color:{_MUTED};font-size:11px;text-transform:uppercase;
                          letter-spacing:1px;margin-bottom:8px;">Watch Outs</div>
              <ul style="margin:0;padding:0;list-style:none;">{watch_outs_html}</ul>
            </div>
          </div>
          <div style="margin-top:20px;padding-top:16px;border-top:1px solid #bfdbfe;">
            <span style="color:{_MUTED};font-size:12px;">Example stack: </span>
            <code style="background:rgba(255,255,255,0.7);padding:4px 10px;border-radius:4px;
                         font-size:12px;color:#1d4ed8;">{pattern["example_stack"]}</code>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
