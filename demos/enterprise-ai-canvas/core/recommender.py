"""Scoring engine — scores capabilities based on active signals."""
from __future__ import annotations
from core.capabilities import CAPABILITY_REGISTRY

STATUS_RECOMMENDED = "recommended"
STATUS_AVAILABLE = "available"
STATUS_NOT_RECOMMENDED = "not_recommended"
STATUS_MANUALLY_ADDED = "manually_added"
STATUS_MANUALLY_REMOVED = "manually_removed"

def score_capability(cap_id: str, active_signals: list[str]) -> int:
    """Score a capability 0-100 based on active signals."""
    cap = CAPABILITY_REGISTRY.get(cap_id)
    if not cap:
        return 50
    score = 50
    fit_hits = len(set(cap["fit_signals"]) & set(active_signals))
    contra_hits = len(set(cap["contra_signals"]) & set(active_signals))
    score += fit_hits * 10
    score -= contra_hits * 15
    return max(0, min(100, score))

def score_all(active_signals: list[str]) -> dict[str, int]:
    """Return scores for all capabilities."""
    return {cap_id: score_capability(cap_id, active_signals) for cap_id in CAPABILITY_REGISTRY}

def get_status(cap_id: str, score: int, manually_added: set, manually_removed: set) -> str:
    if cap_id in manually_removed:
        return STATUS_MANUALLY_REMOVED
    if cap_id in manually_added:
        return STATUS_MANUALLY_ADDED
    if score >= 65:
        return STATUS_RECOMMENDED
    if score >= 40:
        return STATUS_AVAILABLE
    return STATUS_NOT_RECOMMENDED

def detect_pattern(scores: dict[str, int], manually_added: set, manually_removed: set) -> str:
    """Detect the overall architecture pattern from selected capabilities."""
    def is_active(cap_id):
        if cap_id in manually_removed:
            return False
        if cap_id in manually_added:
            return True
        return scores.get(cap_id, 0) >= 65

    has_rag = any(is_active(c) for c in ["naive_rag", "hybrid_search", "knowledge_graph_rag"])
    has_agent = any(is_active(c) for c in ["langgraph", "custom_agent_loop", "crewai"])
    has_multi_agent = any(is_active(c) for c in ["crewai", "langgraph"])
    has_finetuning = is_active("fine_tuned_model")
    has_realtime = any(is_active(c) for c in ["streaming_ingestion", "streaming_api"])

    if has_multi_agent and has_rag:
        return "Multi-Agent RAG"
    if has_agent and has_rag and has_realtime:
        return "Agentic RAG + Real-time"
    if has_agent and has_rag:
        return "Agentic RAG"
    if has_multi_agent:
        return "Multi-Agent System"
    if has_agent:
        return "Tool-Augmented Agent"
    if has_finetuning and has_rag:
        return "Fine-tuned + RAG Hybrid"
    if has_finetuning:
        return "Fine-tuned Domain Model"
    if has_rag:
        return "RAG Pipeline"
    return "Direct Prompting"

def evaluate_interrogation(cap_id: str, answers: dict[int, bool]) -> dict:
    """Evaluate interrogation answers and return verdict."""
    cap = CAPABILITY_REGISTRY.get(cap_id, {})
    questions = cap.get("interrogation", [])
    if not questions:
        return {"verdict": "justified", "reasoning": "No specific concerns for this capability."}

    score = 0
    for i, q in enumerate(questions):
        answer = answers.get(i)
        if answer is None:
            continue
        if answer == q.get("good", True):
            score += 1

    total = len(questions)
    if score >= total * 0.7:
        return {
            "verdict": "justified",
            "reasoning": f"Your answers confirm {cap['name']} is the right fit for your use case."
        }
    elif score >= total * 0.4:
        return {
            "verdict": "maybe",
            "reasoning": f"{cap['name']} could work, but review the trade-offs carefully. Some of your requirements may be better served by an alternative."
        }
    else:
        alternatives = []
        if cap["layer"] == "foundation_models":
            alternatives = ["gpt4o_mini", "claude_haiku"]
        elif cap["layer"] == "memory_context":
            alternatives = ["faiss", "conversation_buffer"]
        alt_text = f" Consider {' or '.join(alternatives)} as lighter alternatives." if alternatives else ""
        return {
            "verdict": "premature",
            "reasoning": f"Based on your answers, {cap['name']} may be over-engineered for this stage.{alt_text}"
        }
