"""Constraint definitions and signal-to-constraint mapping."""
from __future__ import annotations

CONSTRAINT_REGISTRY = {
    # Compliance
    "gdpr_required": {"label": "GDPR / EU Compliance Required", "type": "hard", "category": "Compliance", "description": "Personal data of EU residents must comply with GDPR."},
    "hipaa_required": {"label": "HIPAA Compliance Required", "type": "hard", "category": "Compliance", "description": "Healthcare data requires HIPAA compliance."},
    "data_residency_required": {"label": "Data Residency Constraint", "type": "hard", "category": "Compliance", "description": "Data cannot leave a specific geographic region."},
    "audit_trail_required": {"label": "Audit Trail Required", "type": "hard", "category": "Compliance", "description": "All AI decisions must be logged for regulatory review."},
    "pii_handling_required": {"label": "PII Must Be Protected", "type": "hard", "category": "Compliance", "description": "Personally identifiable information must be masked before LLM processing."},
    # Technical
    "no_external_apis": {"label": "No External API Calls", "type": "hard", "category": "Technical", "description": "All AI processing must stay within the organisation's infrastructure."},
    "on_prem_required": {"label": "On-Premise Deployment Required", "type": "hard", "category": "Technical", "description": "Cannot deploy to public cloud."},
    "sub_second_latency": {"label": "Sub-Second Latency Required", "type": "soft", "category": "Technical", "description": "AI responses must be generated in under 1 second."},
    "high_availability": {"label": "High Availability (99.9%+)", "type": "soft", "category": "Technical", "description": "System must be highly available with minimal downtime."},
    "streaming_output": {"label": "Streaming Output Required", "type": "soft", "category": "Technical", "description": "Responses should stream to the user token-by-token."},
    # Business
    "cost_per_query_critical": {"label": "Cost Per Query is Critical", "type": "soft", "category": "Business", "description": "Must minimise API cost — high volume or tight margin."},
    "open_source_mandate": {"label": "Open Source Mandate", "type": "hard", "category": "Business", "description": "Organisation policy requires open-source components."},
    "vendor_lock_avoidance": {"label": "Avoid Vendor Lock-in", "type": "soft", "category": "Business", "description": "Prefer portable, framework-agnostic, or open-source solutions."},
    "azure_stack_standard": {"label": "Azure is Standard Stack", "type": "soft", "category": "Business", "description": "Organisation is standardised on Microsoft Azure."},
    "time_to_market_critical": {"label": "Fast Time to Market", "type": "soft", "category": "Business", "description": "Must ship quickly — prefer managed services over custom builds."},
    # Operational
    "team_maturity_low": {"label": "Low AI/ML Team Maturity", "type": "soft", "category": "Operational", "description": "Team is new to AI — prefer low-complexity managed solutions."},
    "team_maturity_high": {"label": "High AI/ML Team Maturity", "type": "soft", "category": "Operational", "description": "Experienced ML team can handle complex custom builds."},
    "multi_tenant_required": {"label": "Multi-Tenant Architecture Required", "type": "soft", "category": "Operational", "description": "Multiple customers or teams need isolated AI contexts."},
    "human_oversight_required": {"label": "Human Oversight Required", "type": "soft", "category": "Operational", "description": "High-stakes decisions require human review before acting."},
}

# Maps extracted signals to constraint IDs
SIGNAL_TO_CONSTRAINTS = {
    "gdpr":                     ["gdpr_required", "data_residency_required", "pii_handling_required"],
    "hipaa":                    ["hipaa_required", "pii_handling_required", "audit_trail_required"],
    "sox":                      ["audit_trail_required"],
    "on_prem":                  ["on_prem_required", "no_external_apis"],
    "data_residency":           ["data_residency_required"],
    "high_data_sensitivity":    ["pii_handling_required", "audit_trail_required"],
    "compliance_heavy":         ["audit_trail_required", "pii_handling_required"],
    "ultra_low_latency":        ["sub_second_latency", "streaming_output"],
    "realtime":                 ["streaming_output"],
    "cost_critical":            ["cost_per_query_critical"],
    "high_volume":              ["cost_per_query_critical", "high_availability"],
    "open_source_preferred":    ["open_source_mandate", "vendor_lock_avoidance"],
    "vendor_lock_concern":      ["vendor_lock_avoidance"],
    "existing_azure":           ["azure_stack_standard"],
    "low_team_maturity":        ["team_maturity_low", "time_to_market_critical"],
    "high_team_maturity":       ["team_maturity_high"],
    "external_users":           ["high_availability", "streaming_output", "pii_handling_required"],
    "multi_tenant":             ["multi_tenant_required"],
    "high_stakes_decisions":    ["human_oversight_required", "audit_trail_required"],
}

def signals_to_constraints(signals: list[str]) -> list[str]:
    """Convert a list of signals to a deduplicated list of constraint IDs."""
    constraint_ids = set()
    for signal in signals:
        for cid in SIGNAL_TO_CONSTRAINTS.get(signal, []):
            constraint_ids.add(cid)
    return list(constraint_ids)
