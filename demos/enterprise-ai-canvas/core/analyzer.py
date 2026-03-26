"""GPT-4o problem analyzer — extracts signals and context from a problem statement."""
from __future__ import annotations
import json
from typing import Any

ALL_SIGNALS = [
    "complex_reasoning", "multimodal", "high_quality", "cost_critical", "ultra_low_latency",
    "realtime", "batch_ok", "cloud_ok", "on_prem", "data_residency", "high_data_sensitivity",
    "compliance_heavy", "gdpr", "hipaa", "sox", "external_users", "internal_users",
    "high_volume", "low_scale", "multilingual", "long_context", "structured_data",
    "unstructured_data", "streaming_data", "multi_agent", "stateful_conversation",
    "enterprise_budget", "startup_budget", "low_team_maturity", "high_team_maturity",
    "open_source_preferred", "vendor_lock_concern", "existing_azure", "fine_tuning_viable",
    "knowledge_base_heavy", "grounding_critical", "relationship_heavy", "multi_tenant",
    "high_stakes_decisions", "domain_specific", "consumer_facing", "event_driven",
    "voice_required", "analytics_use_case", "repeated_queries",
    "tool_integration", "document_heavy", "api_integration",
]

SYSTEM_PROMPT = """You are an expert enterprise AI architect. Analyse a business problem statement and extract structured signals.

Return ONLY a valid JSON object with these exact fields:
{
  "industry": "string (e.g. Financial Services, Healthcare, Retail)",
  "use_case_summary": "string — one sentence describing the core AI use case",
  "signals": ["array of signal strings from the provided list that apply"],
  "reasoning": "string — 2-3 sentences explaining your signal choices",
  "scale": "startup|mid_market|enterprise|global",
  "primary_concern": "string — the single most important architectural concern"
}

Only include signals from the provided list. Be selective — only include signals that genuinely apply."""

def analyze_problem(problem: str, openai_client: Any) -> dict:
    """
    Analyse a problem statement and return extracted signals.
    Returns dict with: industry, use_case_summary, signals, reasoning, scale, primary_concern
    """
    signals_list = "\n".join(f"- {s}" for s in ALL_SIGNALS)
    user_prompt = f"""Problem statement: {problem}

Available signals (only use from this list):
{signals_list}

Return JSON only."""

    response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        response_format={"type": "json_object"},
        temperature=0.2,
    )

    raw = response.choices[0].message.content
    result = json.loads(raw)

    # Validate signals are from allowed list
    valid_signals = [s for s in result.get("signals", []) if s in ALL_SIGNALS]
    result["signals"] = valid_signals

    return result
