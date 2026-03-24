# Visakh Sankar — AI Solutions Lab

Live demos of enterprise AI systems, built in public. Each demo makes a concept you'd normally see on a slide actually interactive and testable.

**Site:** [visakhsankar.com](https://visakhsankar.com)

---

## Demos

### 1. RAG Visual Simulator
Upload any PDF or TXT file and watch the full Retrieval-Augmented Generation pipeline run step by step — chunking, embedding, vector retrieval, and answer generation. Every chunk is scored and ranked so you can see exactly why the model answered the way it did.

**Stack:** Python · Streamlit · OpenAI `text-embedding-3-small` · FAISS · GPT-4o-mini

[Live demo](https://visakh-ai-lab-mgbbdk4k9rk8gmkk4ey4tp.streamlit.app/) · [`demos/rag-visual-simulator`](demos/rag-visual-simulator)

---

### 2. AI Architecture Simulator
Describe your enterprise use case in plain language. The system extracts your constraints, streams live architect reasoning via GPT-4o, recommends the best AI pattern from a 12-pattern library, and generates a trade-off radar chart and architecture brief you can share with your team.

**Stack:** Python · Streamlit · GPT-4o · Plotly · JSON pattern library

[Live demo](https://visakh-ai-lab-nzsdsdjsm45vyayjpvgfmk.streamlit.app/) · [`demos/ai-architecture-simulator`](demos/ai-architecture-simulator)

---

### 3. Agent Systems Playground
Watch an AI agent think, choose tools, and reason its way to an answer — every step exposed. The agent has access to web search, a calculator, a summariser, and a memory system. A Multi-Agent mode shows an Orchestrator delegating work to Research, Analysis, and Writer agents in real time.

**Stack:** Python · Streamlit · GPT-4o · Tavily Search API · OpenAI function calling

[Live demo](https://visakh-ai-lab-dnyxly82duv6rrxvvs9r9m.streamlit.app/) · [`demos/agent-systems-playground`](demos/agent-systems-playground)

---

## Structure

```
demos/
├── rag-visual-simulator/        # Demo 1
├── ai-architecture-simulator/   # Demo 2
└── agent-systems-playground/    # Demo 3
app/                             # Next.js site (visakhsankar.com)
```

## Running a demo locally

```bash
cd demos/<demo-name>
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # add your API keys
streamlit run app.py
```

Each demo needs an `OPENAI_API_KEY`. The Agent Systems Playground also needs a `TAVILY_API_KEY`.

---

Built by [Visakh Sankar](https://visakhsankar.com) · [LinkedIn](https://www.linkedin.com/in/visakhsankar/)
