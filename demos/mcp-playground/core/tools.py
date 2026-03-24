"""Tool implementations and registry for MCP Playground."""
from __future__ import annotations

import ast
import operator
import os
from typing import Any, Callable

# ─── Safe Calculator ──────────────────────────────────────────────────────────

_ALLOWED_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.Mod: operator.mod,
    ast.FloorDiv: operator.floordiv,
}


def _safe_eval(node):
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.BinOp):
        op_type = type(node.op)
        if op_type not in _ALLOWED_OPS:
            raise ValueError(f"Operator {op_type.__name__} not allowed")
        left = _safe_eval(node.left)
        right = _safe_eval(node.right)
        return _ALLOWED_OPS[op_type](left, right)
    if isinstance(node, ast.UnaryOp):
        op_type = type(node.op)
        if op_type not in _ALLOWED_OPS:
            raise ValueError(f"Operator {op_type.__name__} not allowed")
        return _ALLOWED_OPS[op_type](_safe_eval(node.operand))
    raise ValueError(f"Unsupported expression node: {type(node).__name__}")


# ─── Tool Functions ───────────────────────────────────────────────────────────

def web_search(query: str, max_results: int = 4) -> str:
    """Search the web using Tavily API."""
    try:
        from tavily import TavilyClient
        api_key = os.getenv("TAVILY_API_KEY")
        if not api_key:
            return "Error: TAVILY_API_KEY not set."
        tc = TavilyClient(api_key=api_key)
        resp = tc.search(query=query, max_results=int(max_results))
        results = resp.get("results", [])
        if not results:
            return "No results found."
        lines = []
        for i, r in enumerate(results, 1):
            lines.append(f"{i}. **{r.get('title', 'No title')}**")
            lines.append(f"   URL: {r.get('url', '')}")
            lines.append(f"   {r.get('content', '')[:300]}")
            lines.append("")
        return "\n".join(lines)
    except Exception as e:
        return f"Search error: {e}"


def calculator(expression: str) -> str:
    """Safely evaluate an arithmetic expression."""
    try:
        tree = ast.parse(expression.strip(), mode="eval")
        result = _safe_eval(tree.body)
        # Format nicely
        if isinstance(result, float) and result.is_integer():
            result = int(result)
        return f"{expression} = {result}"
    except Exception as e:
        return f"Calculation error: {e}"


_WEATHER_DATA = {
    "london": {"temp_c": 14, "temp_f": 57, "condition": "Partly cloudy", "humidity": 72, "wind_kph": 18},
    "new york": {"temp_c": 22, "temp_f": 72, "condition": "Sunny", "humidity": 55, "wind_kph": 12},
    "tokyo": {"temp_c": 19, "temp_f": 66, "condition": "Clear", "humidity": 60, "wind_kph": 8},
    "dubai": {"temp_c": 38, "temp_f": 100, "condition": "Hot and sunny", "humidity": 40, "wind_kph": 15},
    "sydney": {"temp_c": 21, "temp_f": 70, "condition": "Mostly sunny", "humidity": 65, "wind_kph": 20},
    "singapore": {"temp_c": 30, "temp_f": 86, "condition": "Humid with showers", "humidity": 85, "wind_kph": 10},
    "paris": {"temp_c": 16, "temp_f": 61, "condition": "Overcast", "humidity": 70, "wind_kph": 14},
    "san francisco": {"temp_c": 17, "temp_f": 63, "condition": "Foggy morning", "humidity": 80, "wind_kph": 22},
}


def get_weather(city: str) -> str:
    """Get current weather for a city (mock data)."""
    key = city.strip().lower()
    data = _WEATHER_DATA.get(key)
    if not data:
        available = ", ".join(c.title() for c in _WEATHER_DATA)
        return f"Weather data not available for '{city}'. Available cities: {available}."
    return (
        f"Weather in {city.title()}:\n"
        f"  Temperature: {data['temp_c']}°C / {data['temp_f']}°F\n"
        f"  Condition: {data['condition']}\n"
        f"  Humidity: {data['humidity']}%\n"
        f"  Wind: {data['wind_kph']} km/h"
    )


_DB_DATA = {
    "sales": [
        {"region": "North America", "Q1": 4200000, "Q2": 4800000, "Q3": 5100000, "Q4": 6300000},
        {"region": "Europe", "Q1": 2800000, "Q2": 3100000, "Q3": 3400000, "Q4": 3900000},
        {"region": "Asia Pacific", "Q1": 1900000, "Q2": 2400000, "Q3": 2900000, "Q4": 3800000},
        {"region": "Latin America", "Q1": 800000, "Q2": 950000, "Q3": 1100000, "Q4": 1400000},
    ],
    "headcount": [
        {"department": "Engineering", "headcount": 320, "avg_salary_usd": 145000},
        {"department": "Sales", "headcount": 180, "avg_salary_usd": 95000},
        {"department": "Marketing", "headcount": 85, "avg_salary_usd": 88000},
        {"department": "Product", "headcount": 65, "avg_salary_usd": 138000},
        {"department": "Operations", "headcount": 110, "avg_salary_usd": 78000},
        {"department": "Finance", "headcount": 45, "avg_salary_usd": 112000},
    ],
    "products": [
        {"product": "CorePlatform", "arr_usd": 12400000, "growth_pct": 34, "nps": 62},
        {"product": "DataConnector", "arr_usd": 5800000, "growth_pct": 58, "nps": 71},
        {"product": "InsightsDash", "arr_usd": 3200000, "growth_pct": 22, "nps": 55},
        {"product": "AutomateFlow", "arr_usd": 2100000, "growth_pct": 87, "nps": 68},
    ],
}


def query_database(table: str, filter_col: str = "", filter_val: str = "") -> str:
    """Query mock company database tables."""
    tbl = table.strip().lower()
    data = _DB_DATA.get(tbl)
    if data is None:
        available = ", ".join(_DB_DATA.keys())
        return f"Table '{table}' not found. Available tables: {available}."

    rows = data
    if filter_col and filter_val:
        rows = [
            r for r in data
            if str(r.get(filter_col, "")).lower() == filter_val.strip().lower()
        ]

    if not rows:
        return f"No rows found in '{table}' matching {filter_col}={filter_val}."

    # Format as markdown-ish table
    headers = list(rows[0].keys())
    lines = [" | ".join(str(h) for h in headers)]
    lines.append(" | ".join("---" for _ in headers))
    for row in rows:
        lines.append(" | ".join(str(row[h]) for h in headers))
    return f"Table: {table}\n\n" + "\n".join(lines)


def summarise_text(text: str) -> str:
    """Summarise text into bullet points using GPT-4o-mini."""
    try:
        from openai import OpenAI
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Summarise the following text into 3-5 concise bullet points. Start each bullet with •"},
                {"role": "user", "content": text[:4000]},
            ],
            max_tokens=400,
        )
        return resp.choices[0].message.content or "No summary generated."
    except Exception as e:
        return f"Summarise error: {e}"


# ─── Tool Registry ────────────────────────────────────────────────────────────

TOOL_REGISTRY: dict[str, dict] = {
    "web_search": {
        "name": "web_search",
        "description": "Search the web for current information using Tavily.",
        "icon": "🌐",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "The search query"},
                "max_results": {"type": "integer", "description": "Max results to return (default 4)", "default": 4},
            },
            "required": ["query"],
        },
        "fn": web_search,
    },
    "calculator": {
        "name": "calculator",
        "description": "Evaluate arithmetic expressions safely (no code execution).",
        "icon": "🧮",
        "input_schema": {
            "type": "object",
            "properties": {
                "expression": {"type": "string", "description": "The arithmetic expression, e.g. '(12 * 4.5) / 2'"},
            },
            "required": ["expression"],
        },
        "fn": calculator,
    },
    "get_weather": {
        "name": "get_weather",
        "description": "Get current weather conditions for a city.",
        "icon": "🌤️",
        "input_schema": {
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "City name (e.g. London, Tokyo, Dubai)"},
            },
            "required": ["city"],
        },
        "fn": get_weather,
    },
    "query_database": {
        "name": "query_database",
        "description": "Query mock company database. Tables: sales, headcount, products.",
        "icon": "🗄️",
        "input_schema": {
            "type": "object",
            "properties": {
                "table": {"type": "string", "description": "Table name: sales | headcount | products"},
                "filter_col": {"type": "string", "description": "Column to filter on (optional)"},
                "filter_val": {"type": "string", "description": "Value to filter for (optional)"},
            },
            "required": ["table"],
        },
        "fn": query_database,
    },
    "summarise_text": {
        "name": "summarise_text",
        "description": "Summarise a block of text into bullet points using GPT-4o-mini.",
        "icon": "📝",
        "input_schema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "The text to summarise"},
            },
            "required": ["text"],
        },
        "fn": summarise_text,
    },
}


def get_openai_schemas() -> list[dict]:
    """Return tools in OpenAI function-calling format."""
    schemas = []
    for tool in TOOL_REGISTRY.values():
        schemas.append({
            "type": "function",
            "function": {
                "name": tool["name"],
                "description": tool["description"],
                "parameters": tool["input_schema"],
            },
        })
    return schemas
