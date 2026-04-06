"""Architecture diagram generator — interactive HTML diagrams and Mermaid flowcharts."""
from __future__ import annotations
import json
from core.capabilities import CAPABILITY_REGISTRY, LAYER_REGISTRY, get_layers_ordered, get_caps_for_layer
from core.recommender import get_status, STATUS_RECOMMENDED, STATUS_MANUALLY_ADDED, STATUS_MANUALLY_REMOVED


# Mermaid style classes keyed by layer (kept for Mermaid export)
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

# Structured colors for HTML diagram and PDF
LAYER_COLORS = {
    "foundation_models": {"bg": "#0F766E", "border": "#0D9488", "text": "#ffffff"},
    "orchestration":     {"bg": "#1D4ED8", "border": "#3B82F6", "text": "#ffffff"},
    "memory_context":    {"bg": "#7C3AED", "border": "#8B5CF6", "text": "#ffffff"},
    "data_grounding":    {"bg": "#B45309", "border": "#D97706", "text": "#ffffff"},
    "safety_control":    {"bg": "#DC2626", "border": "#EF4444", "text": "#ffffff"},
    "observability":     {"bg": "#4338CA", "border": "#6366F1", "text": "#ffffff"},
    "deployment_scale":  {"bg": "#0369A1", "border": "#0EA5E9", "text": "#ffffff"},
    "integration_ux":    {"bg": "#059669", "border": "#10B981", "text": "#ffffff"},
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


# ─── Shared helpers ──────────────────────────────────────────────────────────

def _get_active_by_layer(scores, manually_added, manually_removed):
    """Return dict mapping layer_id -> list of active capability dicts."""
    active_by_layer = {}
    for layer_id in get_layers_ordered():
        caps = get_caps_for_layer(layer_id)
        active = [c for c in caps
                  if get_status(c["id"], scores.get(c["id"], 50), manually_added, manually_removed)
                  in (STATUS_RECOMMENDED, STATUS_MANUALLY_ADDED)]
        if active:
            active_by_layer[layer_id] = active
    return active_by_layer


def _safe_id(text: str) -> str:
    """Make a Mermaid-safe node ID."""
    return text.replace(" ", "_").replace("-", "_").replace(".", "").replace("/", "_")


# ─── Interactive HTML Diagram ────────────────────────────────────────────────

def generate_html_diagram(
    pattern: str,
    scores: dict[str, int],
    manually_added: set,
    manually_removed: set,
    analysis: dict | None = None,
) -> str:
    """Generate an interactive HTML/CSS/JS architecture diagram."""

    active_by_layer = _get_active_by_layer(scores, manually_added, manually_removed)
    if not active_by_layer:
        return "<div style='color:#94A3B8;text-align:center;padding:40px'>No active capabilities to diagram.</div>"

    # Build ordered list of active layers with their data
    layers_data = []
    for layer_id in get_layers_ordered():
        if layer_id not in active_by_layer:
            continue
        layer = LAYER_REGISTRY[layer_id]
        colors = LAYER_COLORS[layer_id]
        caps = active_by_layer[layer_id]
        cap_names = [c["name"] for c in caps[:4]]
        extra = max(0, len(caps) - 4)
        layers_data.append({
            "id": layer_id,
            "name": layer["name"],
            "icon": layer["icon"],
            "bg": colors["bg"],
            "border": colors["border"],
            "cap_names": cap_names,
            "extra": extra,
            "caps_detail": [
                {"name": c["name"], "icon": c["icon"], "vendor": c["vendor"],
                 "description": c["description"],
                 "cost": c["trade_offs"]["cost"], "quality": c["trade_offs"]["quality"],
                 "latency": c["trade_offs"]["latency"]}
                for c in caps
            ],
        })

    # Build edges from PATTERN_FLOWS, filtered to active layers
    flows = PATTERN_FLOWS.get(pattern, PATTERN_FLOWS["Direct Prompting"])
    active_ids = set(active_by_layer.keys())
    edges = []
    for src, dst, label in flows:
        if src in active_ids and dst in active_ids:
            edges.append({"src": src, "dst": dst, "label": label, "dashed": False})

    # Observability edges
    if "observability" in active_ids:
        for target in ["foundation_models", "orchestration"]:
            if target in active_ids:
                edges.append({"src": target, "dst": "observability", "label": "Logs & Metrics", "dashed": True})

    # Deployment edges
    if "deployment_scale" in active_ids:
        for target in ["foundation_models", "orchestration"]:
            if target in active_ids:
                edges.append({"src": "deployment_scale", "dst": target, "label": "Hosts", "dashed": True})

    layers_json = json.dumps(layers_data)
    edges_json = json.dumps(edges)
    trade_dots = {"low": "#22C55E", "medium": "#EAB308", "high": "#EF4444", "very_high": "#DC2626", "very_low": "#059669"}
    dots_json = json.dumps(trade_dots)

    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ background:#0F172A; font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif; }}
.toolbar {{ display:flex; align-items:center; justify-content:space-between; padding:16px 20px; }}
.toolbar .title {{ font-size:14px; font-weight:700; color:#E2E8F0; }}
.toolbar .badge {{ font-size:10px; font-weight:600; color:#94A3B8; background:#1E293B; padding:2px 8px; border-radius:4px; margin-left:8px; }}
.toolbar .btn {{ background:#1E293B; color:#94A3B8; border:1px solid #334155; border-radius:6px; padding:5px 14px; font-size:11px; font-weight:600; cursor:pointer; display:flex; align-items:center; gap:4px; }}
.toolbar .btn:hover {{ background:#334155; color:#E2E8F0; }}
#diagram-area {{ position:relative; padding:10px 20px 20px; }}
#arrow-svg {{ position:absolute; top:0; left:0; width:100%; height:100%; pointer-events:none; z-index:1; }}
.layer-box {{ position:relative; width:480px; margin:0 auto 0; padding:14px 18px; border-radius:10px; border-width:2px; border-style:solid; z-index:2; cursor:default; transition:transform 0.15s, box-shadow 0.15s; }}
.layer-box:hover {{ transform:scale(1.02); box-shadow:0 4px 20px rgba(0,0,0,0.4); }}
.layer-name {{ font-size:14px; font-weight:700; color:#fff; margin-bottom:4px; }}
.layer-caps {{ font-size:11px; color:rgba(255,255,255,0.8); line-height:1.4; }}
.tooltip {{ display:none; position:absolute; left:calc(50% + 260px); width:280px; background:#1E293B; border:1px solid #334155; border-radius:10px; padding:14px; z-index:20; box-shadow:0 8px 30px rgba(0,0,0,0.5); max-height:320px; overflow-y:auto; }}
.tooltip .tip-title {{ font-size:13px; font-weight:700; color:#E2E8F0; margin-bottom:8px; }}
.tooltip hr {{ border:none; border-top:1px solid #334155; margin:8px 0; }}
.tooltip .tip-cap {{ margin-bottom:10px; }}
.tooltip .tip-cap-name {{ font-size:12px; font-weight:600; color:#F1F5F9; }}
.tooltip .tip-cap-vendor {{ font-size:10px; color:#94A3B8; margin-left:4px; }}
.tooltip .tip-cap-desc {{ font-size:11px; color:#94A3B8; margin-top:2px; line-height:1.4; }}
.tooltip .tip-dots {{ margin-top:4px; display:flex; gap:10px; font-size:10px; color:#CBD5E1; }}
.tooltip .dot {{ width:8px; height:8px; border-radius:50%; display:inline-block; margin-right:3px; vertical-align:middle; }}
.edge-label {{ font-size:10px; fill:#CBD5E1; font-weight:500; pointer-events:none; }}
.edge-label-bg {{ fill:#0F172A; opacity:0.85; }}
.spacer {{ height:50px; }}
</style>
</head><body>
<div class="toolbar">
  <div><span class="title">{pattern}</span><span class="badge">AUTO-GENERATED</span></div>
  <button class="btn" onclick="openFullScreen()">
    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M15 3h6v6M9 21H3v-6M21 3l-7 7M3 21l7-7"/></svg>
    Full Screen
  </button>
</div>
<div id="diagram-area"></div>
<script>
var LAYERS = {layers_json};
var EDGES = {edges_json};
var DOTS = {dots_json};

function buildDiagram() {{
  var area = document.getElementById('diagram-area');
  area.innerHTML = '';

  // Create SVG overlay
  var svg = document.createElementNS('http://www.w3.org/2000/svg','svg');
  svg.id = 'arrow-svg';
  svg.style.cssText = 'position:absolute;top:0;left:0;width:100%;height:100%;pointer-events:none;z-index:1';
  // Arrowhead marker
  var defs = document.createElementNS('http://www.w3.org/2000/svg','defs');
  var marker = document.createElementNS('http://www.w3.org/2000/svg','marker');
  marker.setAttribute('id','ah'); marker.setAttribute('markerWidth','8'); marker.setAttribute('markerHeight','6');
  marker.setAttribute('refX','8'); marker.setAttribute('refY','3'); marker.setAttribute('orient','auto');
  var poly = document.createElementNS('http://www.w3.org/2000/svg','polygon');
  poly.setAttribute('points','0 0, 8 3, 0 6'); poly.setAttribute('fill','#FFFFFF');
  marker.appendChild(poly); defs.appendChild(marker);
  // Dashed arrowhead
  var marker2 = marker.cloneNode(true); marker2.setAttribute('id','ahd');
  marker2.firstChild.setAttribute('fill','#64748B');
  defs.appendChild(marker2);
  svg.appendChild(defs);
  area.appendChild(svg);

  // Build layer position map
  var layerOrder = {{}};
  LAYERS.forEach(function(l, i) {{ layerOrder[l.id] = i; }});

  var BOX_H = 60, GAP = 50, START_Y = 10;
  var totalH = LAYERS.length * BOX_H + (LAYERS.length - 1) * GAP + START_Y + 20;
  area.style.height = totalH + 'px';
  svg.setAttribute('viewBox', '0 0 ' + area.offsetWidth + ' ' + totalH);
  svg.style.height = totalH + 'px';

  // Create layer boxes
  LAYERS.forEach(function(layer, idx) {{
    var box = document.createElement('div');
    box.className = 'layer-box';
    box.id = 'box-' + layer.id;
    box.style.backgroundColor = layer.bg;
    box.style.borderColor = layer.border;
    box.style.marginBottom = (idx < LAYERS.length - 1) ? GAP + 'px' : '0';

    var capsText = layer.cap_names.join(', ');
    if (layer.extra > 0) capsText += ' +' + layer.extra + ' more';

    box.innerHTML = '<div class="layer-name">' + layer.icon + ' ' + layer.name + '</div>' +
                    '<div class="layer-caps">' + capsText + '</div>';

    // Tooltip
    var tip = document.createElement('div');
    tip.className = 'tooltip';
    tip.id = 'tip-' + layer.id;
    var tipHtml = '<div class="tip-title">' + layer.icon + ' ' + layer.name + '</div><hr>';
    layer.caps_detail.forEach(function(c) {{
      tipHtml += '<div class="tip-cap">' +
        '<span class="tip-cap-name">' + c.icon + ' ' + c.name + '</span>' +
        '<span class="tip-cap-vendor">(' + c.vendor + ')</span>' +
        '<div class="tip-cap-desc">' + c.description.substring(0,120) + '</div>' +
        '<div class="tip-dots">' +
        '<span><span class="dot" style="background:' + (DOTS[c.cost]||'#94A3B8') + '"></span>Cost</span>' +
        '<span><span class="dot" style="background:' + (DOTS[c.quality]||'#94A3B8') + '"></span>Quality</span>' +
        '<span><span class="dot" style="background:' + (DOTS[c.latency]||'#94A3B8') + '"></span>Latency</span>' +
        '</div></div>';
    }});
    tip.innerHTML = tipHtml;

    box.addEventListener('mouseenter', function() {{ tip.style.display = 'block'; }});
    box.addEventListener('mouseleave', function() {{ tip.style.display = 'none'; }});

    var wrapper = document.createElement('div');
    wrapper.style.position = 'relative';
    wrapper.appendChild(box);
    wrapper.appendChild(tip);
    area.appendChild(wrapper);
  }});

  // Draw arrows after layout settles
  requestAnimationFrame(function() {{
    var areaRect = area.getBoundingClientRect();
    var W = area.offsetWidth;
    svg.setAttribute('viewBox', '0 0 ' + W + ' ' + totalH);

    // Get center positions of each layer box
    var positions = {{}};
    LAYERS.forEach(function(l) {{
      var el = document.getElementById('box-' + l.id);
      if (!el) return;
      var r = el.getBoundingClientRect();
      positions[l.id] = {{
        cx: r.left - areaRect.left + r.width / 2,
        top: r.top - areaRect.top,
        bottom: r.top - areaRect.top + r.height,
        left: r.left - areaRect.left,
        right: r.left - areaRect.left + r.width
      }};
    }});

    // Track edge pairs for offset
    var pairCount = {{}};
    EDGES.forEach(function(e) {{
      var key = [e.src, e.dst].sort().join('|');
      pairCount[key] = (pairCount[key] || 0) + 1;
    }});
    var pairUsed = {{}};

    EDGES.forEach(function(e) {{
      var sp = positions[e.src], dp = positions[e.dst];
      if (!sp || !dp) return;

      var key = [e.src, e.dst].sort().join('|');
      var idx = pairUsed[key] = (pairUsed[key] || 0);
      pairUsed[key]++;
      var hasPair = pairCount[key] > 1;

      var srcBelow = sp.top > dp.top;
      var x1, y1, x2, y2, offset = 0;

      if (hasPair) {{ offset = idx === 0 ? -40 : 40; }}

      if (srcBelow) {{
        y1 = sp.top; y2 = dp.bottom;
      }} else {{
        y1 = sp.bottom; y2 = dp.top;
      }}
      x1 = sp.cx + offset;
      x2 = dp.cx + offset;

      var path = document.createElementNS('http://www.w3.org/2000/svg','path');
      var midY = (y1 + y2) / 2;

      // Curved path
      var cpx1 = x1 + offset * 0.5, cpx2 = x2 + offset * 0.5;
      var d = 'M ' + x1 + ' ' + y1 + ' C ' + cpx1 + ' ' + midY + ', ' + cpx2 + ' ' + midY + ', ' + x2 + ' ' + y2;

      path.setAttribute('d', d);
      path.setAttribute('fill', 'none');
      path.setAttribute('stroke', e.dashed ? '#64748B' : '#FFFFFF');
      path.setAttribute('stroke-width', e.dashed ? '1.5' : '2');
      if (e.dashed) path.setAttribute('stroke-dasharray', '6,4');
      path.setAttribute('marker-end', e.dashed ? 'url(#ahd)' : 'url(#ah)');
      svg.appendChild(path);

      // Edge label
      var lx = (x1 + x2) / 2 + offset * 0.3;
      var ly = midY;

      // Background rect for label
      var labelText = document.createElementNS('http://www.w3.org/2000/svg','text');
      labelText.setAttribute('x', lx); labelText.setAttribute('y', ly);
      labelText.setAttribute('text-anchor', 'middle'); labelText.setAttribute('dominant-baseline', 'middle');
      labelText.setAttribute('class', 'edge-label');
      labelText.textContent = e.label;
      // Measure text width by appending temporarily
      svg.appendChild(labelText);
      var bbox = labelText.getBBox();
      svg.removeChild(labelText);

      var bg = document.createElementNS('http://www.w3.org/2000/svg','rect');
      bg.setAttribute('x', bbox.x - 4); bg.setAttribute('y', bbox.y - 2);
      bg.setAttribute('width', bbox.width + 8); bg.setAttribute('height', bbox.height + 4);
      bg.setAttribute('rx', '3'); bg.setAttribute('class', 'edge-label-bg');
      svg.appendChild(bg);
      svg.appendChild(labelText);
    }});
  }});
}}

function openFullScreen() {{
  var w = window.open('', '_blank');
  var html = document.documentElement.outerHTML;
  // Remove the fullscreen button in the new window, add zoom controls instead
  w.document.write('<!DOCTYPE html><html><head><meta charset="utf-8"><title>{pattern}</title>' +
    '<style>' +
    '* {{ margin:0;padding:0;box-sizing:border-box }}' +
    'body {{ background:#0F172A;font-family:-apple-system,BlinkMacSystemFont,sans-serif }}' +
    '.fs-toolbar {{ position:fixed;top:0;left:0;right:0;padding:12px 24px;background:#0F172A;border-bottom:1px solid #1E293B;z-index:100;display:flex;align-items:center;justify-content:space-between }}' +
    '.fs-toolbar h1 {{ color:#E2E8F0;font-size:16px;font-weight:700 }}' +
    '.fs-toolbar .badge {{ font-size:10px;font-weight:600;color:#94A3B8;background:#1E293B;padding:2px 8px;border-radius:4px;margin-left:8px }}' +
    '.fs-controls {{ display:flex;gap:8px }}' +
    '.fs-controls button {{ background:#1E293B;color:#E2E8F0;border:1px solid #334155;border-radius:6px;padding:6px 14px;font-size:12px;font-weight:600;cursor:pointer }}' +
    '.fs-controls button:hover {{ background:#334155 }}' +
    '.fs-canvas {{ margin-top:52px;padding:30px;overflow:auto;display:flex;justify-content:center }}' +
    '.fs-inner {{ transform-origin:top center;transition:transform 0.2s }}' +
    '</style></head><body>' +
    '<div class="fs-toolbar"><div style="display:flex;align-items:center"><h1>{pattern}</h1><span class="badge">AUTO-GENERATED</span></div>' +
    '<div class="fs-controls"><button onclick="z(0.8)">- Zoom Out</button><button onclick="z(1.25)">+ Zoom In</button><button onclick="r()">Reset</button></div></div>' +
    '<div class="fs-canvas"><div class="fs-inner" id="fs-inner"></div></div>' +
    '<script>var sc=1;function z(f){{sc*=f;document.getElementById("fs-inner").style.transform="scale("+sc+")"}}function r(){{sc=1;document.getElementById("fs-inner").style.transform="scale(1)"}}<\\/script>' +
    '</body></html>');
  w.document.close();
  // Copy diagram content into the fullscreen window
  setTimeout(function() {{
    var src = document.getElementById('diagram-area');
    var dest = w.document.getElementById('fs-inner');
    if (src && dest) {{
      dest.innerHTML = src.innerHTML;
      // Rebuild arrows in the new context
      var script = w.document.createElement('script');
      script.textContent = 'var LAYERS=' + JSON.stringify(LAYERS) + ';var EDGES=' + JSON.stringify(EDGES) + ';var DOTS=' + JSON.stringify(DOTS) + ';(' + buildDiagram.toString() + ')();';
      w.document.body.appendChild(script);
    }}
  }}, 100);
}}

buildDiagram();
</script>
</body></html>"""


# ─── Mermaid export (kept for copy/paste) ────────────────────────────────────

def generate_mermaid(
    pattern: str,
    scores: dict[str, int],
    manually_added: set,
    manually_removed: set,
    analysis: dict | None = None,
) -> str:
    """Generate a Mermaid flowchart from the canvas state."""
    active_by_layer = _get_active_by_layer(scores, manually_added, manually_removed)

    lines = ["graph TD"]

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

    flows = PATTERN_FLOWS.get(pattern, PATTERN_FLOWS["Direct Prompting"])
    active_layer_ids = set(active_by_layer.keys())

    for src_layer, dst_layer, edge_label in flows:
        src_id = _safe_id(src_layer)
        dst_id = _safe_id(dst_layer)
        if src_layer in active_layer_ids and dst_layer in active_layer_ids:
            lines.append(f'    {src_id} -->|"{edge_label}"| {dst_id}')

    if "observability" in active_by_layer:
        obs_id = _safe_id("observability")
        for target in ["foundation_models", "orchestration"]:
            if target in active_layer_ids:
                lines.append(f'    {_safe_id(target)} -.->|"Logs & Metrics"| {obs_id}')

    if "deployment_scale" in active_by_layer:
        dep_id = _safe_id("deployment_scale")
        for target in ["foundation_models", "orchestration"]:
            if target in active_layer_ids:
                lines.append(f'    {dep_id} -.->|"Hosts"| {_safe_id(target)}')

    lines.append("")

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
    """Generate a plain-text summary of the architecture."""
    active_by_layer = _get_active_by_layer(scores, manually_added, manually_removed)

    # Use name-only for summary
    name_by_layer = {lid: [c["name"] for c in caps] for lid, caps in active_by_layer.items()}
    total = sum(len(v) for v in name_by_layer.values())
    layers_used = len(name_by_layer)

    summary = f"**Pattern:** {pattern}  \n"
    summary += f"**Stack:** {total} capabilities across {layers_used} layers  \n\n"

    for layer_id, names in name_by_layer.items():
        layer = LAYER_REGISTRY[layer_id]
        summary += f"**{layer['icon']} {layer['name']}:** {', '.join(names)}  \n"

    return summary


# ─── Architecture Comparison ─────────────────────────────────────────────────

def compute_diff(snap_a: dict, snap_b: dict) -> dict:
    """Compare two architecture snapshots and return structured diff."""
    active_a = _get_active_by_layer(snap_a["scores"], snap_a["manually_added"], snap_a["manually_removed"])
    active_b = _get_active_by_layer(snap_b["scores"], snap_b["manually_added"], snap_b["manually_removed"])

    caps_a = {c["id"] for caps in active_a.values() for c in caps}
    caps_b = {c["id"] for caps in active_b.values() for c in caps}

    # Per-layer diff
    all_layers = set(list(active_a.keys()) + list(active_b.keys()))
    layer_diffs = {}
    for lid in get_layers_ordered():
        if lid not in all_layers:
            continue
        a_ids = {c["id"] for c in active_a.get(lid, [])}
        b_ids = {c["id"] for c in active_b.get(lid, [])}
        added = b_ids - a_ids
        removed = a_ids - b_ids
        unchanged = a_ids & b_ids
        if added or removed:
            layer_diffs[lid] = {"added": added, "removed": removed, "unchanged": unchanged}

    return {
        "pattern_a": snap_a.get("pattern", "Unknown"),
        "pattern_b": snap_b.get("pattern", "Unknown"),
        "pattern_changed": snap_a.get("pattern") != snap_b.get("pattern"),
        "caps_added": caps_b - caps_a,
        "caps_removed": caps_a - caps_b,
        "caps_unchanged": caps_a & caps_b,
        "total_a": len(caps_a),
        "total_b": len(caps_b),
        "constraints_added": snap_b.get("active_constraints", set()) - snap_a.get("active_constraints", set()),
        "constraints_removed": snap_a.get("active_constraints", set()) - snap_b.get("active_constraints", set()),
        "layer_diffs": layer_diffs,
    }
