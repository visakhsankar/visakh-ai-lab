"""MCP Concepts — visual explanation of the Model Context Protocol."""
from __future__ import annotations

import streamlit as st

PURPLE = "#7C3AED"
PURPLE_LIGHT = "#EDE9FE"
PURPLE_BORDER = "#C4B5FD"
TEXT = "#1e293b"
MUTED = "#64748b"
CARD_BORDER = "#e2e8f0"

st.markdown(
    """
    <style>
      .block-container { padding-top: 3rem; padding-bottom: 2rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ─── Header ───────────────────────────────────────────────────────────────────
st.markdown('<h1 style="font-size:2.2rem;font-weight:800;color:#1e293b;margin-bottom:2px">📚 How MCP Works</h1>', unsafe_allow_html=True)
st.markdown('<p style="font-size:16px;color:#64748b;margin-bottom:2px">A visual guide to the Model Context Protocol — the USB standard for AI tools.</p>', unsafe_allow_html=True)
st.markdown('<p style="font-size:12px;color:#94a3b8">by <a href="https://visakhsankar.com" style="color:#7C3AED;text-decoration:none;font-weight:600">Visakh Sankar</a></p>', unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# ─── Section 1: The Big Idea ──────────────────────────────────────────────────
st.markdown('<div style="font-size:11px;font-weight:800;color:#7C3AED;text-transform:uppercase;letter-spacing:1.5px;margin-bottom:8px">THE BIG IDEA</div>', unsafe_allow_html=True)

st.markdown(
    '<div style="background:linear-gradient(135deg,#EDE9FE,#F5F3FF);border:1px solid #C4B5FD;border-radius:14px;padding:24px 28px;margin-bottom:24px">'
    '<div style="font-size:18px;font-weight:700;color:#1e293b;margin-bottom:12px">MCP is USB-C for AI tools.</div>'
    '<div style="font-size:14px;color:#374151;line-height:1.8">Before MCP, every AI application had to build custom integrations for every tool. Connecting to Slack meant writing Slack-specific code. Connecting to a database meant more custom code. And none of it was reusable.<br><br>MCP defines a <strong>single universal protocol</strong> so any AI model can connect to any tool server — without knowing what tools exist ahead of time. The AI discovers what\'s available at runtime, through the protocol itself.</div>'
    '</div>',
    unsafe_allow_html=True,
)

# ─── Section 2: The 4 Actors ──────────────────────────────────────────────────
st.markdown('<div style="font-size:11px;font-weight:800;color:#7C3AED;text-transform:uppercase;letter-spacing:1.5px;margin:24px 0 8px">THE 4 ACTORS</div>', unsafe_allow_html=True)

actors = [
    ("🤖", "Host", "Your application — e.g. Claude Desktop, this Streamlit app, an IDE. The host starts and manages MCP sessions."),
    ("📡", "Client", "Lives inside the Host. Sends JSON-RPC 2.0 requests, logs every message, matches request IDs to responses. One client per server connection."),
    ("⚙️", "Server", "Receives requests and routes them to the right tool. In production this is a separate process or remote service. In this demo it runs in-process."),
    ("🔧", "Tools", "The actual functions that do real work: web search, calculator, database queries, weather lookups, text summarisation, etc."),
]

cols = st.columns(4)
for col, (icon, title, desc) in zip(cols, actors):
    with col:
        st.markdown(
            f'<div style="background:#ffffff;border:1px solid #e2e8f0;border-radius:12px;padding:16px;height:100%">'
            f'<div style="font-size:32px;margin-bottom:8px">{icon}</div>'
            f'<div style="font-size:13px;font-weight:700;color:#1e293b;margin-bottom:6px">{title}</div>'
            f'<div style="font-size:12px;color:#64748b;line-height:1.6">{desc}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

st.markdown("<br>", unsafe_allow_html=True)

# ─── Section 3: The 3 Protocol Phases ────────────────────────────────────────
st.markdown('<div style="font-size:11px;font-weight:800;color:#7C3AED;text-transform:uppercase;letter-spacing:1.5px;margin:16px 0 8px">THE 3 PROTOCOL PHASES</div>', unsafe_allow_html=True)

phases = [
    {
        "num": "01",
        "title": "Handshake",
        "method": "initialize",
        "color": "#3B82F6",
        "bg": "#EFF6FF",
        "border": "#BFDBFE",
        "desc": "The client introduces itself and the server declares its capabilities. Both sides agree on the protocol version. This happens once at the start of every session.",
        "request": '{\n  "jsonrpc": "2.0",\n  "method": "initialize",\n  "params": {\n    "protocolVersion": "2024-11-05",\n    "clientInfo": { "name": "mcp-client" }\n  },\n  "id": 1\n}',
        "response": '{\n  "jsonrpc": "2.0",\n  "result": {\n    "serverInfo": { "name": "mcp-server" },\n    "capabilities": { "tools": {} }\n  },\n  "id": 1\n}',
    },
    {
        "num": "02",
        "title": "Discovery",
        "method": "tools/list",
        "color": "#8B5CF6",
        "bg": "#F5F3FF",
        "border": "#DDD6FE",
        "desc": "The client asks the server what tools exist. The server returns every tool's name, description, and input schema. The AI host uses these schemas to know how to call each tool.",
        "request": '{\n  "jsonrpc": "2.0",\n  "method": "tools/list",\n  "params": {},\n  "id": 2\n}',
        "response": '{\n  "jsonrpc": "2.0",\n  "result": {\n    "tools": [\n      { "name": "web_search", ... },\n      { "name": "calculator", ... }\n    ]\n  },\n  "id": 2\n}',
    },
    {
        "num": "03",
        "title": "Execution",
        "method": "tools/call",
        "color": "#059669",
        "bg": "#F0FDF4",
        "border": "#BBF7D0",
        "desc": "The AI model (GPT-4o) decides which tool to call based on the task. It outputs the tool name and arguments as structured JSON. The client routes this through MCP to the server, which runs the tool and returns the result.",
        "request": '{\n  "jsonrpc": "2.0",\n  "method": "tools/call",\n  "params": {\n    "name": "calculator",\n    "arguments": { "expression": "18 - 12" }\n  },\n  "id": 5\n}',
        "response": '{\n  "jsonrpc": "2.0",\n  "result": {\n    "content": [\n      { "type": "text", "text": "6" }\n    ]\n  },\n  "id": 5\n}',
    },
]

for phase in phases:
    st.markdown(
        f'<div style="background:{phase["bg"]};border:1px solid {phase["border"]};border-radius:14px;padding:20px 24px;margin-bottom:16px">'
        f'<div style="display:flex;align-items:center;gap:12px;margin-bottom:12px">'
        f'<span style="background:{phase["color"]};color:#fff;font-size:11px;font-weight:800;padding:4px 10px;border-radius:6px;letter-spacing:0.5px">{phase["num"]}</span>'
        f'<span style="font-size:16px;font-weight:700;color:#1e293b">{phase["title"]}</span>'
        f'<span style="font-size:12px;font-family:monospace;background:rgba(0,0,0,0.06);padding:3px 8px;border-radius:4px;color:{phase["color"]}">{phase["method"]}</span>'
        f'</div>'
        f'<p style="font-size:13px;color:#374151;line-height:1.7;margin-bottom:14px">{phase["desc"]}</p>'
        f'</div>',
        unsafe_allow_html=True,
    )
    col_req, col_resp = st.columns(2)
    with col_req:
        req_escaped = phase["request"].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        st.markdown(
            f'<div style="background:#ffffff;border:1px solid {phase["border"]};border-radius:8px;padding:12px 14px">'
            f'<div style="font-size:10px;font-weight:700;color:{phase["color"]};text-transform:uppercase;letter-spacing:0.5px;margin-bottom:6px">→ Request</div>'
            f'<pre style="font-size:11px;color:#1e293b;margin:0;line-height:1.5;white-space:pre-wrap;word-break:break-all">{req_escaped}</pre>'
            f'</div>',
            unsafe_allow_html=True,
        )
    with col_resp:
        resp_escaped = phase["response"].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        st.markdown(
            f'<div style="background:#ffffff;border:1px solid {phase["border"]};border-radius:8px;padding:12px 14px">'
            f'<div style="font-size:10px;font-weight:700;color:#059669;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:6px">← Response</div>'
            f'<pre style="font-size:11px;color:#1e293b;margin:0;line-height:1.5;white-space:pre-wrap;word-break:break-all">{resp_escaped}</pre>'
            f'</div>',
            unsafe_allow_html=True,
        )
    st.markdown("<br>", unsafe_allow_html=True)

# ─── Section 4: This Demo vs Production ──────────────────────────────────────
st.markdown('<div style="font-size:11px;font-weight:800;color:#7C3AED;text-transform:uppercase;letter-spacing:1.5px;margin:8px 0 8px">THIS DEMO VS PRODUCTION MCP</div>', unsafe_allow_html=True)

st.markdown(
    """
    <table style="width:100%;border-collapse:collapse;font-size:13px;margin-bottom:16px">
      <thead>
        <tr style="background:#f8fafc">
          <th style="padding:10px 14px;text-align:left;border:1px solid #e2e8f0;color:#64748b;font-weight:700">Aspect</th>
          <th style="padding:10px 14px;text-align:center;border:1px solid #e2e8f0;color:#7C3AED;font-weight:700">This Demo</th>
          <th style="padding:10px 14px;text-align:center;border:1px solid #e2e8f0;color:#059669;font-weight:700">Production (e.g. Claude Desktop)</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td style="padding:9px 14px;border:1px solid #e2e8f0;font-weight:500">Server location</td>
          <td style="padding:9px 14px;border:1px solid #e2e8f0;text-align:center">In-process (same Python process)</td>
          <td style="padding:9px 14px;border:1px solid #e2e8f0;text-align:center">Separate process or remote server</td>
        </tr>
        <tr style="background:#f8fafc">
          <td style="padding:9px 14px;border:1px solid #e2e8f0;font-weight:500">Transport</td>
          <td style="padding:9px 14px;border:1px solid #e2e8f0;text-align:center">Direct Python function call</td>
          <td style="padding:9px 14px;border:1px solid #e2e8f0;text-align:center">stdio / HTTP / SSE</td>
        </tr>
        <tr>
          <td style="padding:9px 14px;border:1px solid #e2e8f0;font-weight:500">Number of servers</td>
          <td style="padding:9px 14px;border:1px solid #e2e8f0;text-align:center">1 server, 5 tools</td>
          <td style="padding:9px 14px;border:1px solid #e2e8f0;text-align:center">Many servers (GitHub, Slack, DB, etc.)</td>
        </tr>
        <tr style="background:#f8fafc">
          <td style="padding:9px 14px;border:1px solid #e2e8f0;font-weight:500">Protocol messages</td>
          <td style="padding:9px 14px;border:1px solid #e2e8f0;text-align:center">Logged and shown to you</td>
          <td style="padding:9px 14px;border:1px solid #e2e8f0;text-align:center">Hidden (but identical format)</td>
        </tr>
        <tr>
          <td style="padding:9px 14px;border:1px solid #e2e8f0;font-weight:500">Purpose</td>
          <td style="padding:9px 14px;border:1px solid #e2e8f0;text-align:center">Education — see inside the protocol</td>
          <td style="padding:9px 14px;border:1px solid #e2e8f0;text-align:center">Production — speed and reliability</td>
        </tr>
      </tbody>
    </table>
    """,
    unsafe_allow_html=True,
)

# ─── Section 5: Real World Ecosystem ─────────────────────────────────────────
st.markdown('<div style="font-size:11px;font-weight:800;color:#7C3AED;text-transform:uppercase;letter-spacing:1.5px;margin:16px 0 8px">THE REAL-WORLD ECOSYSTEM</div>', unsafe_allow_html=True)

st.markdown(
    '<div style="background:#ffffff;border:1px solid #e2e8f0;border-radius:14px;padding:20px 24px;margin-bottom:16px">'
    '<div style="font-size:13px;color:#374151;line-height:1.8;margin-bottom:16px">When you use Claude Desktop with MCP enabled, it creates one MCP client per connected server. All tool schemas are merged and the AI can call any of them.</div>'
    '<div style="font-family:monospace;font-size:12px;background:#f8fafc;border:1px solid #e2e8f0;border-radius:8px;padding:14px 18px;line-height:2;color:#1e293b">'
    'Claude Desktop<br>'
    '&nbsp;&nbsp;&nbsp;&nbsp;├── MCPClient ←→ <span style="color:#7C3AED;font-weight:700">github-server</span> &nbsp;&nbsp;&nbsp;(search_repos, create_pr, read_file)<br>'
    '&nbsp;&nbsp;&nbsp;&nbsp;├── MCPClient ←→ <span style="color:#7C3AED;font-weight:700">postgres-server</span> &nbsp;(run_query, list_tables)<br>'
    '&nbsp;&nbsp;&nbsp;&nbsp;├── MCPClient ←→ <span style="color:#7C3AED;font-weight:700">slack-server</span> &nbsp;&nbsp;&nbsp;&nbsp;(read_messages, post_message)<br>'
    '&nbsp;&nbsp;&nbsp;&nbsp;└── MCPClient ←→ <span style="color:#7C3AED;font-weight:700">filesystem-server</span> (read_file, write_file)'
    '</div>'
    '<div style="font-size:12px;color:#64748b;margin-top:12px;line-height:1.6">The AI sees all tools from all servers merged into one list. It doesn\'t know or care which server a tool lives on — it just says <code>tools/call → run_query</code> and the right client routes it automatically.</div>'
    '</div>',
    unsafe_allow_html=True,
)

# ─── Footer CTA ───────────────────────────────────────────────────────────────
st.markdown(
    '<div style="background:linear-gradient(135deg,#7C3AED,#6D28D9);border-radius:14px;padding:24px 28px;text-align:center;margin-top:16px">'
    '<div style="font-size:16px;font-weight:700;color:#ffffff;margin-bottom:8px">Now go try it live</div>'
    '<div style="font-size:13px;color:#DDD6FE;line-height:1.6">Head to the MCP Playground tab, type any question, and watch every protocol message appear in real time.<br>Then try Before vs After to see exactly what MCP adds.</div>'
    '</div>',
    unsafe_allow_html=True,
)
