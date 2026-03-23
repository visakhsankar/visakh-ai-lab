"""
Tool implementations for the Agent Systems Playground.
Each tool takes plain args and returns a string result.
"""
import ast
import operator
import os
import time

import streamlit as st

# ── Shared helpers ─────────────────────────────────────────────────────────────

def _openai_key() -> str:
    return os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY", "")

def _tavily_key() -> str:
    return os.getenv("TAVILY_API_KEY") or st.secrets.get("TAVILY_API_KEY", "")


# ── Web Search ─────────────────────────────────────────────────────────────────

def web_search(query: str) -> str:
    """Search the web using Tavily API."""
    api_key = _tavily_key()
    if not api_key:
        return "Error: TAVILY_API_KEY not configured."
    try:
        from tavily import TavilyClient
        client = TavilyClient(api_key=api_key)
        results = client.search(query, max_results=3, search_depth="basic")
        if not results.get("results"):
            return "No results found for that query."
        parts = []
        for r in results["results"]:
            parts.append(
                f"**{r.get('title', 'Untitled')}**\n"
                f"Source: {r.get('url', '')}\n"
                f"{r.get('content', '')[:600]}"
            )
        return "\n\n---\n\n".join(parts)
    except Exception as e:
        return f"Search error: {e}"


# ── Calculator ─────────────────────────────────────────────────────────────────

_SAFE_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.Mod: operator.mod,
}


def _eval_node(node):
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.BinOp):
        return _SAFE_OPS[type(node.op)](_eval_node(node.left), _eval_node(node.right))
    if isinstance(node, ast.UnaryOp):
        return _SAFE_OPS[type(node.op)](_eval_node(node.operand))
    raise ValueError(f"Unsupported operation: {type(node).__name__}")


def calculator(expression: str) -> str:
    """Safely evaluate a mathematical expression."""
    try:
        tree = ast.parse(expression.strip(), mode="eval")
        result = _eval_node(tree.body)
        if isinstance(result, float) and result == int(result):
            result = int(result)
        formatted = f"{result:,.2f}" if isinstance(result, float) else f"{result:,}"
        return f"{expression} = {formatted}"
    except ZeroDivisionError:
        return "Error: Division by zero."
    except Exception as e:
        return f"Error evaluating '{expression}': {e}"


# ── Memory ─────────────────────────────────────────────────────────────────────

_LT_KEY = "_agent_long_term_memory"   # persists across page navigation in session
_ST_KEY = "_agent_short_term_memory"  # cleared on new run


def remember(key: str, value: str) -> str:
    """Store a fact in long-term memory."""
    if _LT_KEY not in st.session_state:
        st.session_state[_LT_KEY] = {}
    st.session_state[_LT_KEY][key] = {
        "value": value,
        "stored_at": time.strftime("%H:%M:%S"),
    }
    return f"Stored in memory — '{key}': {value}"


def recall(key: str = "") -> str:
    """Retrieve facts from long-term memory."""
    mem = st.session_state.get(_LT_KEY, {})
    if not mem:
        return "Long-term memory is empty."
    if key:
        entry = mem.get(key)
        return f"{key}: {entry['value']}" if entry else f"No memory for key: '{key}'"
    return "\n".join(f"• {k}: {v['value']}" for k, v in mem.items())


# ── Summariser ─────────────────────────────────────────────────────────────────

def summarise(url_or_text: str) -> str:
    """Summarise a URL or long text into bullet points."""
    from openai import OpenAI
    client = OpenAI(api_key=_openai_key())

    text = url_or_text
    if url_or_text.strip().startswith("http"):
        try:
            from tavily import TavilyClient
            tc = TavilyClient(api_key=_tavily_key())
            result = tc.extract(urls=[url_or_text.strip()])
            if result.get("results"):
                text = result["results"][0].get("raw_content", url_or_text)[:4000]
        except Exception:
            pass  # fall back to summarising the URL string itself

    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Summarise the following in 3-5 clear bullet points. Be concise and factual."},
                {"role": "user", "content": text[:4000]},
            ],
            max_tokens=400,
        )
        return resp.choices[0].message.content
    except Exception as e:
        return f"Summarise error: {e}"


# ── Dispatcher ─────────────────────────────────────────────────────────────────

def execute_tool(name: str, args: dict) -> str:
    """Route a tool call by name to its implementation."""
    dispatch = {
        "web_search": lambda: web_search(args.get("query", "")),
        "calculator":  lambda: calculator(args.get("expression", "")),
        "remember":    lambda: remember(args.get("key", ""), args.get("value", "")),
        "recall":      lambda: recall(args.get("key", "")),
        "summarise":   lambda: summarise(args.get("url_or_text", "")),
    }
    fn = dispatch.get(name)
    if fn:
        return fn()
    return f"Unknown tool: '{name}'"
