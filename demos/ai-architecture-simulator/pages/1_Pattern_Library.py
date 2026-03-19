"""
Pattern Library — browse all 12 AI architecture patterns.
"""
import os
import sys
import pathlib
import json
import streamlit as st
import plotly.graph_objects as go

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

# ─── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Pattern Library · AI Architecture Simulator",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── Shared palette ───────────────────────────────────────────────────────────
_GREEN  = "#22c55e"
_BLUE   = "#3b82f6"
_AMBER  = "#f59e0b"
_RED    = "#ef4444"
_PURPLE = "#a855f7"
_TEXT   = "#1e293b"
_MUTED  = "#64748b"
_LIGHT  = "#f1f5f9"
_BORDER = "#e2e8f0"

# ─── CSS ──────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    .stApp { background-color: #f8fafc; }
    hr { border-color: #e2e8f0 !important; margin: 20px 0 !important; }
    details { border: 1px solid #e2e8f0 !important; border-radius: 8px !important; background: #fff !important; }
    div[data-testid="stButton"] > button {
        background: #3b82f6 !important; color: white !important;
        border: none !important; border-radius: 6px !important;
        font-weight: 600 !important; font-size: 13px !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ─── Load patterns ────────────────────────────────────────────────────────────
@st.cache_data
def load_patterns():
    lib_path = pathlib.Path(__file__).parent.parent / "patterns" / "library.json"
    with open(lib_path) as f:
        return json.load(f)["patterns"]

patterns = load_patterns()

# ─── Complexity / skill mapping ───────────────────────────────────────────────
SKILL_ORDER  = {"beginner": 1, "intermediate": 2, "advanced": 3, "expert": 4}
SKILL_COLOR  = {"beginner": _GREEN, "intermediate": _AMBER, "advanced": _BLUE, "expert": _PURPLE}
SKILL_LABEL  = {"beginner": "🟢 Beginner", "intermediate": "🟡 Intermediate",
                "advanced": "🔵 Advanced", "expert": "🟣 Expert"}

# ─── Header ───────────────────────────────────────────────────────────────────
st.markdown(
    f'<h1 style="color:{_TEXT};font-size:2.2rem;font-weight:800;margin-bottom:4px;">📚 Pattern Library</h1>',
    unsafe_allow_html=True,
)
st.markdown(
    f'<p style="color:{_MUTED};font-size:1.05rem;margin-bottom:12px;">'
    f"All <strong>{len(patterns)}</strong> AI architecture patterns — scores, trade-offs, stacks, and when to use each one.</p>",
    unsafe_allow_html=True,
)
st.markdown(
    f"""
    <div style="display:inline-flex;align-items:center;gap:8px;background:#eff6ff;
                border:1px solid #bfdbfe;border-radius:20px;padding:6px 16px;margin-bottom:4px;">
      <span style="font-size:14px;">🚀</span>
      <span style="font-size:13px;color:#1d4ed8;font-weight:600;">Starter Pack</span>
      <span style="font-size:13px;color:{_MUTED};">— {len(patterns)} patterns included · more being added regularly</span>
    </div>
    """,
    unsafe_allow_html=True,
)
st.markdown("---")

# ─── Filters ──────────────────────────────────────────────────────────────────
f_col1, f_col2, f_col3 = st.columns([1, 1, 2])

with f_col1:
    skill_options = ["All"] + ["🟢 Beginner", "🟡 Intermediate", "🔵 Advanced", "🟣 Expert"]
    skill_filter  = st.selectbox("Team Skill", skill_options)

with f_col2:
    cost_options = ["All", "Low", "Medium", "High"]
    cost_filter  = st.selectbox("Cost Level", cost_options)

with f_col3:
    search = st.text_input("🔍  Search patterns", placeholder="e.g. graph, fine-tuning, privacy…")

# Apply filters
def matches(p: dict) -> bool:
    if skill_filter != "All":
        target = skill_filter.split(" ", 1)[1].lower()
        if p.get("min_team_skill", "") != target:
            return False
    if cost_filter != "All":
        c = p.get("cost", "").lower()
        if cost_filter == "Low"   and "low"    not in c: return False
        if cost_filter == "Medium" and "medium" not in c: return False
        if cost_filter == "High"  and ("high" not in c and "very" not in c): return False
    if search:
        needle = search.lower()
        haystack = (
            p.get("name", "") + " " +
            p.get("tagline", "") + " " +
            p.get("description", "") + " " +
            " ".join(p.get("best_for", []))
        ).lower()
        if needle not in haystack:
            return False
    return True

visible = [p for p in patterns if matches(p)]
st.markdown(
    f'<p style="color:{_MUTED};font-size:13px;margin-bottom:16px;">'
    f'Showing <strong>{len(visible)}</strong> of {len(patterns)} patterns</p>',
    unsafe_allow_html=True,
)

# ─── Sort by complexity ───────────────────────────────────────────────────────
visible.sort(key=lambda p: SKILL_ORDER.get(p.get("min_team_skill", "beginner"), 1))

# ─── Mini radar helper ────────────────────────────────────────────────────────
def mini_radar(pattern: dict) -> go.Figure:
    categories = ["Accuracy", "Speed", "Privacy", "Cost Eff.", "Scalability", "Simplicity"]
    score_keys = ["accuracy", "speed", "privacy", "cost_efficiency", "scalability", "simplicity"]
    scores     = [pattern["scores"].get(k, 0) for k in score_keys]
    scores_c   = scores + [scores[0]]
    cats_c     = categories + [categories[0]]

    fig = go.Figure(go.Scatterpolar(
        r=scores_c, theta=cats_c,
        fill="toself",
        line=dict(color=_BLUE, width=2),
        fillcolor="rgba(59,130,246,0.12)",
    ))
    fig.update_layout(
        polar=dict(
            bgcolor="rgba(248,250,252,0.9)",
            radialaxis=dict(visible=True, range=[0, 5], showticklabels=False,
                            gridcolor=_BORDER, linecolor=_BORDER),
            angularaxis=dict(tickfont=dict(size=9, color=_MUTED), linecolor=_BORDER),
        ),
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=220,
        margin=dict(l=40, r=40, t=10, b=10),
    )
    return fig

# ─── Score bar helper ─────────────────────────────────────────────────────────
def score_bars(scores: dict) -> str:
    keys   = ["accuracy", "speed", "privacy", "cost_efficiency", "scalability", "simplicity"]
    labels = ["Accuracy", "Speed", "Privacy", "Cost Eff.", "Scalability", "Simplicity"]
    rows   = ""
    for k, label in zip(keys, labels):
        v    = scores.get(k, 0)
        pct  = v / 5 * 100
        color = _GREEN if v >= 4 else (_AMBER if v >= 3 else _RED)
        rows += (
            f'<div style="display:flex;align-items:center;gap:8px;margin-bottom:5px;">'
            f'<span style="width:80px;font-size:11px;color:{_MUTED};flex-shrink:0;">{label}</span>'
            f'<div style="flex:1;background:{_LIGHT};border-radius:4px;height:8px;">'
            f'<div style="width:{pct}%;background:{color};border-radius:4px;height:8px;"></div></div>'
            f'<span style="width:16px;font-size:11px;font-weight:700;color:{color};">{v}</span>'
            f'</div>'
        )
    return rows

# ─── Pattern cards grid ───────────────────────────────────────────────────────
if not visible:
    st.info("No patterns match your filters. Try adjusting them.")
else:
    for i in range(0, len(visible), 2):
        row_patterns = visible[i: i + 2]
        cols = st.columns(len(row_patterns))

        for col, p in zip(cols, row_patterns):
            skill     = p.get("min_team_skill", "beginner")
            s_color   = SKILL_COLOR.get(skill, _MUTED)
            s_label   = SKILL_LABEL.get(skill, skill)
            best_html = "".join(
                f'<li style="font-size:12px;color:{_TEXT};margin-bottom:3px;">✓ {b}</li>'
                for b in p.get("best_for", [])[:3]
            )
            weak_html = "".join(
                f'<li style="font-size:12px;color:{_MUTED};margin-bottom:3px;">· {w}</li>'
                for w in p.get("weaknesses", [])[:2]
            )

            with col:
                # Card — fixed min-height keeps paired cards even
                st.markdown(
                    f"""
                    <div style="background:#fff;border:1px solid {_BORDER};border-radius:12px;
                                padding:18px 20px;box-shadow:0 2px 6px rgba(0,0,0,0.04);
                                margin-bottom:4px;min-height:540px;
                                display:flex;flex-direction:column;">
                      <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:10px;">
                        <div>
                          <h3 style="margin:0 0 3px 0;color:{_TEXT};font-size:17px;">{p["name"]}</h3>
                          <p style="color:{_MUTED};margin:0;font-size:12px;font-style:italic;">{p["tagline"]}</p>
                        </div>
                        <span style="background:{s_color}18;border:1px solid {s_color};border-radius:20px;
                                     padding:3px 10px;font-size:11px;font-weight:700;color:{s_color};
                                     white-space:nowrap;flex-shrink:0;margin-left:8px;">{s_label}</span>
                      </div>
                      <p style="color:#374151;font-size:13px;line-height:1.6;margin-bottom:12px;
                                min-height:60px;">{p["description"]}</p>
                      <div style="display:flex;gap:16px;margin-bottom:12px;">
                        <span style="font-size:12px;color:{_TEXT};">⏱️ {p["build_time"]}</span>
                        <span style="font-size:12px;color:{_TEXT};">👥 {p["team_needs"].split("+")[0].strip()}</span>
                      </div>
                      <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:10px;min-height:90px;">
                        <div>
                          <div style="font-size:11px;color:{_MUTED};text-transform:uppercase;
                                      letter-spacing:1px;margin-bottom:5px;">Best for</div>
                          <ul style="margin:0;padding:0;list-style:none;">{best_html}</ul>
                        </div>
                        <div>
                          <div style="font-size:11px;color:{_MUTED};text-transform:uppercase;
                                      letter-spacing:1px;margin-bottom:5px;">Weaknesses</div>
                          <ul style="margin:0;padding:0;list-style:none;">{weak_html}</ul>
                        </div>
                      </div>
                      <div style="margin-top:auto;padding-top:8px;">
                        {score_bars(p["scores"])}
                      </div>
                      <div style="margin-top:10px;padding-top:10px;border-top:1px solid {_BORDER};">
                        <code style="background:{_LIGHT};padding:4px 8px;border-radius:4px;
                                     font-size:11px;color:#1d4ed8;">{p["example_stack"]}</code>
                      </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                # Expandable radar
                with st.expander(f"📊 {p['name']} — trade-off radar"):
                    st.plotly_chart(mini_radar(p), use_container_width=True)
                    st.markdown(
                        f'<p style="color:{_MUTED};font-size:11px;text-align:center;">'
                        "Higher = better on all axes (1–5 scale)</p>",
                        unsafe_allow_html=True,
                    )

# ─── Summary comparison table ─────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    f'<h3 style="color:{_TEXT};">📋 Quick Comparison Table</h3>',
    unsafe_allow_html=True,
)

header = (
    f'<tr style="background:{_LIGHT};">'
    f'<th style="padding:10px 12px;text-align:left;color:{_MUTED};font-size:11px;text-transform:uppercase;letter-spacing:1px;">Pattern</th>'
    f'<th style="padding:10px 12px;text-align:center;color:{_MUTED};font-size:11px;text-transform:uppercase;letter-spacing:1px;">Accuracy</th>'
    f'<th style="padding:10px 12px;text-align:center;color:{_MUTED};font-size:11px;text-transform:uppercase;letter-spacing:1px;">Speed</th>'
    f'<th style="padding:10px 12px;text-align:center;color:{_MUTED};font-size:11px;text-transform:uppercase;letter-spacing:1px;">Privacy</th>'
    f'<th style="padding:10px 12px;text-align:center;color:{_MUTED};font-size:11px;text-transform:uppercase;letter-spacing:1px;">Cost Eff.</th>'
    f'<th style="padding:10px 12px;text-align:left;color:{_MUTED};font-size:11px;text-transform:uppercase;letter-spacing:1px;">Build Time</th>'
    f'<th style="padding:10px 12px;text-align:left;color:{_MUTED};font-size:11px;text-transform:uppercase;letter-spacing:1px;">Skill Needed</th>'
    f'</tr>'
)


def score_dot(v: int) -> str:
    color = _GREEN if v >= 4 else (_AMBER if v == 3 else _RED)
    return f'<span style="color:{color};font-size:16px;font-weight:700;">{v}/5</span>'


rows_html = ""
for p in sorted(patterns, key=lambda x: SKILL_ORDER.get(x.get("min_team_skill", "beginner"), 1)):
    s      = p["scores"]
    skill  = p.get("min_team_skill", "beginner")
    sc     = SKILL_COLOR.get(skill, _MUTED)
    rows_html += (
        f'<tr style="border-top:1px solid {_BORDER};">'
        f'<td style="padding:10px 12px;color:{_TEXT};font-weight:600;white-space:nowrap;">{p["name"]}</td>'
        f'<td style="padding:10px 12px;text-align:center;">{score_dot(s.get("accuracy",0))}</td>'
        f'<td style="padding:10px 12px;text-align:center;">{score_dot(s.get("speed",0))}</td>'
        f'<td style="padding:10px 12px;text-align:center;">{score_dot(s.get("privacy",0))}</td>'
        f'<td style="padding:10px 12px;text-align:center;">{score_dot(s.get("cost_efficiency",0))}</td>'
        f'<td style="padding:10px 12px;font-size:13px;color:{_MUTED};">{p["build_time"]}</td>'
        f'<td style="padding:10px 12px;">'
        f'<span style="background:{sc}18;color:{sc};border-radius:12px;padding:2px 8px;'
        f'font-size:11px;font-weight:700;text-transform:capitalize;">{skill}</span></td>'
        f'</tr>'
    )

st.markdown(
    f"""
    <div style="overflow-x:auto;">
    <table style="width:100%;border-collapse:collapse;background:#fff;border:1px solid {_BORDER};
                  border-radius:10px;overflow:hidden;">
      <thead>{header}</thead>
      <tbody>{rows_html}</tbody>
    </table>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    f'<p style="color:#94a3b8;font-size:12px;text-align:center;margin-top:24px;">'
    "Built by Visakh Sankar · visakhsankar.com</p>",
    unsafe_allow_html=True,
)
