from typing import List

import streamlit as st

# ─── Pipeline Stages ─────────────────────────────────────────────────────────
# Each tuple: (emoji, label)
_STAGES = [
    ("📄", "Upload"),
    ("✂️", "Chunk & Embed"),
    ("🔍", "Retrieve"),
    ("💬", "Answer"),
]

# pipeline_stage values used by app.py:
#   0 → nothing done
#   1 → file uploaded (processing)
#   2 → chunks + index built
#   3 → chunks retrieved
#   4 → answer generated


def _dot_bar(filled: int, total: int = 5, color: str = "#22c55e") -> str:
    """Return filled/empty dot string for similarity display."""
    dots = "●" * filled + "○" * (total - filled)
    return f'<span style="color:{color};letter-spacing:2px">{dots}</span>'


def _similarity_color(score: float) -> str:
    if score >= 0.6:
        return "#22c55e"  # green
    if score >= 0.35:
        return "#f59e0b"  # amber
    return "#ef4444"  # red


def render_pipeline(pipeline_stage: int) -> None:
    """Render a horizontal pipeline flow diagram showing RAG stages.

    pipeline_stage: 0=none, 1=processing, 2=indexed, 3=retrieved, 4=answered
    """
    # Map pipeline_stage to which stage index is "active" (0-indexed)
    # done = all stages with index < done_up_to
    done_up_to = pipeline_stage - 1  # stages with index <= done_up_to-1 are complete

    stages_html = ""
    for i, (icon, label) in enumerate(_STAGES):
        if i < done_up_to:
            bg, fg, inner = "#22c55e", "#fff", "✓"
            label_color = "#15803d"
        elif i == done_up_to:
            bg, fg, inner = "#3b82f6", "#fff", icon
            label_color = "#1d4ed8"
        else:
            bg, fg, inner = "#f1f5f9", "#94a3b8", icon
            label_color = "#94a3b8"

        stages_html += f"""
        <div style="display:flex;flex-direction:column;align-items:center;gap:6px">
          <div style="width:48px;height:48px;border-radius:50%;background:{bg};color:{fg};
                      display:flex;align-items:center;justify-content:center;
                      font-size:{18 if inner == '✓' else 20}px;font-weight:700;
                      box-shadow:0 2px 6px rgba(0,0,0,0.1)">
            {inner}
          </div>
          <span style="font-size:11px;font-weight:600;color:{label_color};
                       text-align:center;max-width:72px;line-height:1.3">{label}</span>
        </div>
        """
        if i < len(_STAGES) - 1:
            arrow_color = "#22c55e" if i < done_up_to else "#cbd5e1"
            stages_html += f"""
            <div style="color:{arrow_color};font-size:22px;margin:0 2px;
                        padding-bottom:20px;align-self:flex-start;padding-top:13px">
              &#8594;
            </div>
            """

    st.markdown(
        f"""
        <div style="background:linear-gradient(135deg,#f8fafc,#f1f5f9);
                    border:1px solid #e2e8f0;border-radius:14px;
                    padding:20px 32px;display:flex;align-items:flex-start;
                    justify-content:center;flex-wrap:wrap;gap:4px;margin:12px 0 20px">
          {stages_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


# ─── Chunk Cards ─────────────────────────────────────────────────────────────

def render_chunk_cards(retrieved: List[dict]) -> None:
    """Render retrieved chunks as ranked, color-coded cards."""
    for item in retrieved:
        sim = item["similarity"]
        color = _similarity_color(sim)
        dots = _dot_bar(round(sim * 5), color=color)
        rank_labels = {1: "🥇", 2: "🥈", 3: "🥉"}
        rank_icon = rank_labels.get(item["rank"], f"#{item['rank']}")

        # Truncate long chunks for display
        preview = item["chunk_text"]
        truncated = len(preview) > 600
        display_text = preview[:600] + ("…" if truncated else "")

        st.markdown(
            f"""
            <div style="background:#fff;border:1px solid #e2e8f0;border-radius:12px;
                        padding:18px 22px;margin-bottom:12px;
                        border-left:4px solid {color}">
              <div style="display:flex;align-items:center;
                          justify-content:space-between;margin-bottom:10px">
                <div style="display:flex;align-items:center;gap:10px">
                  <span style="font-size:22px">{rank_icon}</span>
                  <span style="font-weight:700;color:#1e293b;font-size:15px">
                    Chunk {item['chunk_index']}
                  </span>
                  <span style="background:#f1f5f9;border-radius:6px;padding:2px 8px;
                               font-size:12px;color:#64748b">
                    Rank #{item['rank']}
                  </span>
                </div>
                <div style="text-align:right">
                  {dots}
                  <div style="font-size:12px;color:{color};font-weight:600;margin-top:2px">
                    Relevance {sim:.2f}
                  </div>
                  <div style="font-size:11px;color:#94a3b8">
                    L2 dist {item['distance']:.4f}
                  </div>
                </div>
              </div>
              <div style="font-size:13.5px;color:#374151;line-height:1.7;
                          background:#f8fafc;border-radius:8px;padding:12px;
                          font-family:Georgia,serif">
                {display_text}
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ─── Answer Card ─────────────────────────────────────────────────────────────

def render_answer_card(answer: str, retrieved: List[dict] | None = None) -> None:
    """Render the generated answer in a polished card."""
    source_ids = ""
    if retrieved:
        ids = ", ".join(f"Chunk {r['chunk_index']}" for r in retrieved)
        source_ids = f"""
        <div style="margin-top:16px;padding-top:12px;border-top:1px solid #e2e8f0;
                    font-size:12px;color:#64748b">
          📎 <strong>Sources used:</strong> {ids}
        </div>
        """

    st.markdown(
        f"""
        <div style="background:linear-gradient(135deg,#eff6ff,#dbeafe);
                    border:1px solid #bfdbfe;border-radius:14px;
                    padding:24px 28px;margin-top:8px">
          <div style="font-size:13px;font-weight:700;color:#1d4ed8;
                      letter-spacing:0.05em;margin-bottom:12px">
            💡 GENERATED ANSWER
          </div>
          <div style="font-size:15.5px;color:#1e293b;line-height:1.8;
                      font-family:Georgia,serif">
            {answer.replace(chr(10), "<br>")}
          </div>
          {source_ids}
        </div>
        """,
        unsafe_allow_html=True,
    )
