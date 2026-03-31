"""Architecture diagram generator — produces Mermaid flowcharts from canvas results."""
from __future__ import annotations
from core.capabilities import CAPABILITY_REGISTRY, LAYER_REGISTRY, get_layers_ordered, get_caps_for_layer
from core.recommender import get_status, STATUS_RECOMMENDED, STATUS_MANUALLY_ADDED, STATUS_MANUALLY_REMOVED


# Mermaid style classes keyed by layer
LAYER_STYLES = {
    "foundation_models": "fill:#0F766E,stroke:#0D9488,color:#fff",
    "orchestration":     "fill:#1D4ED8,stroke:#3B82F6,color:#fff",
    "memory_context":    "fill:#7C3AED,stroke:#8B5CF6,color:#fff",
    "data_grounding":    "fill:#B45309,stroke:#D97706,color:#fff",
    "safety_control":    "fill:#DC2626,stroke:#EF4444,color:#fff",
    "observability":     "fill:#4338CA,stroke:#6366F1,color:#fff",
    "deployment_scale":  "fill:#0369A1,stroke:#0EA5E9,color:#fff",
    "integration_ux":    "fill:#059669,stroke:#10B981,color:#fff",
}

# How data flows between layers in different patterns
PATTERN_FLOWS = {
    "RAG Pipeline": [
        ("integration_ux", "orchestration", "User Query"),
        ("orchestration", "data_grounding", "Retrieve"),
        ("data_grounding", "memory_context", "Vector Search"),
        ("memory_context", "data_grounding", "Relevant Chunks"),
        ("data_grounding", "foundation_models", "Context + Query"),
        ("foundation_models", "safety_control", "Response"),
        ("safety_control", "integration_ux", "Answer"),
    ],
    "Agentic RAG": [
        ("integration_ux", "orchestration", "User Query"),
        ("orchestration", "foundation_models", "Reason & Plan"),
        ("foundation_models", "orchestration", "Tool Call"),
        ("orchestration", "data_grounding", "Retrieve"),
        ("data_grounding", "memory_context", "Vector Search"),
        ("orchestration", "foundation_models", "Context + Query"),
        ("foundation_models", "safety_control", "Response"),
        ("safety_control", "integration_ux", "Answer"),
    ],
    "Agentic RAG + Real-time": [
        ("integration_ux", "orchestration", "User Query"),
        ("orchestration", "foundation_models", "Reason & Plan"),
        ("foundation_models", "orchestration", "Tool Call"),
        ("orchestration", "data_grounding", "Retrieve / Stream"),
        ("data_grounding", "memory_context", "Vector Search"),
        ("orchestration", "foundation_models", "Context + Query"),
        ("foundation_models", "safety_control", "Streaming Response"),
        ("safety_control", "integration_ux", "Answer"),
    ],
    "Multi-Agent RAG": [
        ("integration_ux", "orchestration", "User Query"),
        ("orchestration", "foundation_models", "Route to Agent"),
        ("foundation_models", "orchestration", "Agent Decision"),
        ("orchestration", "data_grounding", "Retrieve"),
        ("data_grounding", "memory_context", "Vector Search"),
        ("orchestration", "foundation_models", "Agent 2: Synthesize"),
        ("foundation_models", "safety_control", "Response"),
        ("safety_control", "integration_ux", "Answer"),
    ],
    "Multi-Agent System": [
        ("integration_ux", "orchestration", "User Task"),
        ("orchestration", "foundation_models", "Route to Agent"),
        ("foundation_models", "orchestration", "Agent Action"),
        ("orchestration", "foundation_models", "Agent 2: Process"),
        ("foundation_models", "orchestration", "Result"),
        ("orchestration", "safety_control", "Final Output"),
        ("safety_control", "integration_ux", "Response"),
    ],
    "Tool-Augmented Agent": [
        ("integration_ux", "orchestration", "User Query"),
        ("orchestration", "foundation_models", "Reason"),
        ("foundation_models", "orchestration", "Tool Call"),
        ("orchestration", "integration_ux", "Execute Tool"),
        ("orchestration", "foundation_models", "Tool Result"),
        ("foundation_models", "safety_control", "Response"),
        ("safety_control", "integration_ux", "Answer"),
    ],
    "Fine-tuned + RAG Hybrid": [
        ("integration_ux", "orchestration", "User Query"),
        ("orchestration", "data_grounding", "Retrieve"),
        ("data_grounding", "memory_context", "Vector Search"),
        ("orchestration", "foundation_models", "Fine-tuned Inference"),
        ("foundation_models", "safety_control", "Response"),
        ("safety_control", "integration_ux", "Answer"),
    ],
    "Fine-tuned Domain Model": [
        ("integration_ux", "orchestration", "User Query"),
        ("orchestration", "foundation_models", "Fine-tuned Inference"),
        ("foundation_models", "safety_control", "Response"),
        ("safety_control", "integration_ux", "Answer"),
    ],
    "Direct Prompting": [
        ("integration_ux", "foundation_models", "User Query"),
        ("foundation_models", "safety_control", "Response"),
        ("safety_control", "integration_ux", "Answer"),
    ],
}


def _safe_id(text: str) -> str:
    """Make a Mermaid-safe node ID."""
    return text.replace(" ", "_").replace("-", "_").replace(".", "").replace("/", "_")


def generate_mermaid(
    pattern: str,
    scores: dict[str, int],
    manually_added: set,
    manually_removed: set,
    analysis: dict | None = None,
) -> str:
    """Generate a Mermaid flowchart from the canvas state."""

    # Collect active capabilities per layer
    active_by_layer: dict[str, list[dict]] = {}
    for layer_id in get_layers_ordered():
        caps = get_caps_for_layer(layer_id)
        active = []
        for c in caps:
            status = get_status(c["id"], scores.get(c["id"], 50), manually_added, manually_removed)
            if status in (STATUS_RECOMMENDED, STATUS_MANUALLY_ADDED):
                active.append(c)
        if active:
            active_by_layer[layer_id] = active

    # Start building the Mermaid diagram
    lines = ["graph TD"]

    # Add node definitions grouped by layer using subgraphs
    for layer_id in get_layers_ordered():
        if layer_id not in active_by_layer:
            continue
        layer = LAYER_REGISTRY[layer_id]
        caps = active_by_layer[layer_id]
        cap_names = ", ".join(c["name"] for c in caps[:4])
        if len(caps) > 4:
            cap_names += f" +{len(caps)-4}"

        node_id = _safe_id(layer_id)
        label = f"{layer['icon']} {layer['name']}\\n{cap_names}"
        lines.append(f'    {node_id}["{label}"]')

    # Add edges based on pattern
    flows = PATTERN_FLOWS.get(pattern, PATTERN_FLOWS["Direct Prompting"])
    active_layer_ids = set(active_by_layer.keys())

    # Filter flows to only include layers that have active capabilities
    # But always include the flow if both endpoints exist
    for src_layer, dst_layer, edge_label in flows:
        src_id = _safe_id(src_layer)
        dst_id = _safe_id(dst_layer)
        # Only add edge if both layers have active capabilities
        if src_layer in active_layer_ids and dst_layer in active_layer_ids:
            lines.append(f'    {src_id} -->|"{edge_label}"| {dst_id}')

    # Add observability as a monitoring connection if present
    if "observability" in active_by_layer:
        obs_id = _safe_id("observability")
        # Connect observability to foundation_models and orchestration if they exist
        for target in ["foundation_models", "orchestration"]:
            if target in active_layer_ids:
                lines.append(f'    {_safe_id(target)} -.->|"Logs & Metrics"| {obs_id}')

    # Add deployment as infrastructure note if present
    if "deployment_scale" in active_by_layer:
        dep_id = _safe_id("deployment_scale")
        for target in ["foundation_models", "orchestration"]:
            if target in active_layer_ids:
                lines.append(f'    {dep_id} -.->|"Hosts"| {_safe_id(target)}')

    lines.append("")

    # Add style classes
    for layer_id in active_by_layer:
        node_id = _safe_id(layer_id)
        style = LAYER_STYLES.get(layer_id, "fill:#334155,stroke:#475569,color:#fff")
        lines.append(f"    style {node_id} {style}")

    return "\n".join(lines)


def generate_diagram_summary(
    pattern: str,
    scores: dict[str, int],
    manually_added: set,
    manually_removed: set,
    analysis: dict | None = None,
) -> str:
    """Generate a plain-text summary of the architecture for display alongside the diagram."""
    active_by_layer: dict[str, list[str]] = {}
    for layer_id in get_layers_ordered():
        caps = get_caps_for_layer(layer_id)
        active = []
        for c in caps:
            status = get_status(c["id"], scores.get(c["id"], 50), manually_added, manually_removed)
            if status in (STATUS_RECOMMENDED, STATUS_MANUALLY_ADDED):
                active.append(c["name"])
        if active:
            active_by_layer[layer_id] = active

    total = sum(len(v) for v in active_by_layer.values())
    layers_used = len(active_by_layer)

    summary = f"**Pattern:** {pattern}  \n"
    summary += f"**Stack:** {total} capabilities across {layers_used} layers  \n\n"

    for layer_id, names in active_by_layer.items():
        layer = LAYER_REGISTRY[layer_id]
        summary += f"**{layer['icon']} {layer['name']}:** {', '.join(names)}  \n"

    return summary
