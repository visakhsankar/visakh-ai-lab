import os

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

from rag.chunker import chunk_text
from rag.extractor import extract_text
from rag.generator import generate_answer
from rag.retriever import build_index, retrieve_chunks
from ui.components import render_answer_card, render_chunk_cards, render_pipeline

load_dotenv()

# ─── Page Config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="RAG Visual Simulator",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Minimal CSS tweaks — keep Streamlit's native feel, just tighten spacing
st.markdown(
    """
    <style>
      .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }
      [data-testid="stMetricValue"] { font-size: 1.6rem; font-weight: 700; }
      [data-testid="stMetricLabel"] { font-size: 0.75rem; color: #64748b; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ─── API Key Guard ────────────────────────────────────────────────────────────
if not os.getenv("OPENAI_API_KEY"):
    st.error("⚠️ **OPENAI_API_KEY** is missing. Add it to your `.env` file and restart.")
    st.stop()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ─── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Pipeline Settings")
    st.divider()

    chunk_size = st.slider(
        "Chunk Size (chars)",
        min_value=200,
        max_value=2000,
        value=1000,
        step=100,
        help="How many characters go into each chunk. Smaller = more granular retrieval.",
    )
    overlap = st.slider(
        "Chunk Overlap (chars)",
        min_value=0,
        max_value=500,
        value=200,
        step=50,
        help="Characters shared between adjacent chunks. Prevents answers from being cut at boundaries.",
    )
    top_k = st.slider(
        "Top K Retrieval",
        min_value=1,
        max_value=10,
        value=3,
        help="How many chunks to pass to the LLM as context.",
    )

    st.divider()
    st.markdown(
        """
        **How RAG works:**
        1. Split document into overlapping chunks
        2. Embed each chunk as a vector
        3. Embed the question
        4. Retrieve nearest chunks by vector distance
        5. Feed context + question to an LLM
        """,
        help="Retrieval-Augmented Generation grounds LLM answers in source material.",
    )
    st.divider()
    st.caption("RAG Visual Simulator · v2.0")
    st.caption("by [Visakh Sankar](https://visakhsankar.com)")

# ─── Header ──────────────────────────────────────────────────────────────────
st.title("🔍 RAG Visual Simulator")
st.caption(
    "Upload any PDF or TXT file, then watch how Retrieval-Augmented Generation "
    "chunks, embeds, retrieves, and answers — step by step."
)
st.divider()

# ─── Session State Init ───────────────────────────────────────────────────────
_SS_KEYS = ["chunks", "index", "embeddings", "raw_text", "chunk_settings"]
for k in _SS_KEYS:
    if k not in st.session_state:
        st.session_state[k] = None

# ─── Upload ───────────────────────────────────────────────────────────────────
uploaded_file = st.file_uploader(
    "📄 Upload a PDF or TXT file",
    type=["pdf", "txt"],
    help="Your file is processed locally — nothing is stored.",
)

# Detect when we need to re-process (new file or changed chunk settings)
settings_key = (
    uploaded_file.name if uploaded_file else None,
    chunk_size,
    overlap,
)
needs_reindex = (
    uploaded_file is not None
    and st.session_state.chunk_settings != settings_key
)

if needs_reindex:
    for k in ["chunks", "index", "embeddings", "raw_text"]:
        st.session_state[k] = None
    st.session_state.chunk_settings = settings_key

# ─── Process Document ─────────────────────────────────────────────────────────
if uploaded_file and st.session_state.chunks is None:
    with st.spinner("📖 Extracting text…"):
        raw_text = extract_text(uploaded_file)

    if not raw_text.strip():
        st.error("Could not extract text from this file. Try a different PDF or a plain TXT.")
        st.stop()

    chunks = chunk_text(raw_text, chunk_size=chunk_size, overlap=overlap)

    with st.spinner(f"🔢 Embedding {len(chunks)} chunks via OpenAI…"):
        index, embeddings = build_index(client, chunks)

    st.session_state.raw_text = raw_text
    st.session_state.chunks = chunks
    st.session_state.index = index
    st.session_state.embeddings = embeddings
    st.rerun()

# ─── Compute Pipeline Stage ───────────────────────────────────────────────────
# 0=nothing, 1=file selected (processing), 2=indexed, 3=retrieved, 4=answered
pipeline_stage = 0
if uploaded_file:
    pipeline_stage = 1
if st.session_state.chunks is not None:
    pipeline_stage = 2

# ─── Main Content (once index is ready) ──────────────────────────────────────
if st.session_state.chunks is not None:
    chunks = st.session_state.chunks
    embeddings = st.session_state.embeddings
    raw_text = st.session_state.raw_text

    # Stats row
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📝 Characters", f"{len(raw_text):,}")
    c2.metric("✂️ Chunks", str(len(chunks)))
    c3.metric("🔢 Embedding Dim", str(embeddings.shape[1]))
    c4.metric("📏 Avg Chunk", f"{len(raw_text) // len(chunks):,} chars")

    st.divider()

    # Text + Chunk previews side by side
    col_text, col_chunks = st.columns(2)

    with col_text:
        with st.expander("📄 Extracted Text Preview", expanded=False):
            st.text_area(
                "",
                raw_text[:4000],
                height=240,
                label_visibility="collapsed",
                disabled=True,
            )
            if len(raw_text) > 4000:
                st.caption(f"Showing first 4,000 of {len(raw_text):,} characters.")

    with col_chunks:
        with st.expander(f"✂️ Chunk Preview  ({len(chunks)} chunks total)", expanded=False):
            for i, chunk in enumerate(chunks[:6]):
                st.markdown(
                    f"**Chunk {i}** &nbsp;·&nbsp; "
                    f"<span style='color:#64748b;font-size:12px'>{len(chunk):,} chars</span>",
                    unsafe_allow_html=True,
                )
                st.caption(chunk[:280] + ("…" if len(chunk) > 280 else ""))
                if i < min(5, len(chunks) - 1):
                    st.markdown("---")

    st.divider()

    # ─── Question ────────────────────────────────────────────────────────────
    st.subheader("💬 Ask a Question")
    question = st.text_input(
        "",
        placeholder="e.g. What are the main findings? What does the document say about X?",
        label_visibility="collapsed",
    )

    if question:
        # Retrieve
        with st.spinner("🔍 Retrieving relevant chunks…"):
            retrieved = retrieve_chunks(
                client, question, chunks, st.session_state.index, top_k=top_k
            )
        pipeline_stage = 3

        # Generate answer
        with st.spinner("💬 Generating answer…"):
            answer = generate_answer(client, question, retrieved)
        pipeline_stage = 4

    # Pipeline visualization — rendered after stage is finalised
    render_pipeline(pipeline_stage)

    if question:
        # ── Retrieved Chunks ─────────────────────────────────────────────────
        st.subheader(f"🎯 Top {top_k} Retrieved Chunks")
        st.caption(
            "Chunks are ranked by vector similarity to your question. "
            "Higher relevance score = closer match in embedding space."
        )
        render_chunk_cards(retrieved)

        st.divider()

        # ── Answer ──────────────────────────────────────────────────────────
        st.subheader("📋 Generated Answer")
        render_answer_card(answer, retrieved)

else:
    # No file yet — show pipeline in initial state
    render_pipeline(pipeline_stage)
    st.info(
        "👆 Upload a PDF or TXT file to get started. "
        "Try a research paper, a product spec, or any text-heavy document."
    )
