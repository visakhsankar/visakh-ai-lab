import json
import os
import pathlib
from openai import OpenAI
from typing import Generator

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


def load_pattern_library() -> list:
    """Load the pattern library from JSON file."""
    lib_path = pathlib.Path(__file__).parent.parent / "patterns" / "library.json"
    with open(lib_path) as f:
        return json.load(f)["patterns"]


def _patterns_summary(patterns: list) -> list:
    """Return a lightweight summary of patterns for prompts."""
    return [
        {
            "id": p["id"],
            "name": p["name"],
            "tagline": p["tagline"],
            "best_for": p["best_for"],
            "not_suitable_for": p["not_suitable_for"],
            "latency": p["latency"],
            "cost": p["cost"],
            "privacy_support": p["privacy_support"],
            "min_team_skill": p["min_team_skill"],
            "build_time": p["build_time"]
        }
        for p in patterns
    ]


REASONING_PROMPT = """You are a world-class enterprise AI architect. A client needs help choosing the right AI architecture pattern.

## Client Constraints:
{constraints}

## Available Patterns:
{patterns}

Analyze step-by-step like a senior architect would in a whiteboard session:

**🔍 Reading the constraints...**
[Identify the 2-3 constraints that matter most here and why]

**❌ Eliminating poor fits...**
[Which patterns are immediately ruled out and the specific reason — be direct]

**📊 Scoring the remaining candidates...**
[Walk through the top contenders, weighing the trade-offs]

**✅ Recommendation**
[State your top pick clearly and the one-line reason it wins over the alternatives]

Be concise. An enterprise architect is reading this — no fluff. Use specific pattern names.
"""

STRUCTURED_PROMPT = """You are an enterprise AI architect. Based on the constraints and available patterns, provide a structured recommendation.

## Client Constraints:
{constraints}

## Available Patterns:
{patterns}

Return a JSON object with this EXACT structure:
{{
  "recommended": {{
    "pattern_id": "exact id from library",
    "confidence": 85,
    "primary_reason": "one-line specific reason this is the best fit"
  }},
  "alternatives": [
    {{
      "pattern_id": "exact id from library",
      "rank": 2,
      "reason": "why this is a viable second choice"
    }},
    {{
      "pattern_id": "exact id from library",
      "rank": 3,
      "reason": "why this is a viable third choice"
    }}
  ],
  "rejected": [
    {{
      "pattern_id": "exact id",
      "rejection_reason": "specific constraint that rules this out"
    }}
  ],
  "key_trade_offs": [
    "Trade-off 1: e.g. You gain X but sacrifice Y",
    "Trade-off 2",
    "Trade-off 3"
  ],
  "implementation_watch_outs": [
    "Watch-out 1: the most common failure mode",
    "Watch-out 2"
  ],
  "estimated_timeline": "X-Y weeks",
  "estimated_team_size": "X engineers"
}}

Include at least 4 rejected patterns. Return ONLY valid JSON.
"""


def stream_reasoning(constraints: dict, patterns: list) -> Generator[str, None, None]:
    """Stream the architect's reasoning process token by token."""
    stream = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": REASONING_PROMPT.format(
                    constraints=json.dumps(constraints, indent=2),
                    patterns=json.dumps(_patterns_summary(patterns), indent=2)
                )
            }
        ],
        stream=True,
        temperature=0.3,
        max_tokens=800
    )
    for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta


def get_structured_recommendation(constraints: dict, patterns: list) -> dict:
    """Get the structured JSON recommendation for rendering cards and charts."""
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": STRUCTURED_PROMPT.format(
                    constraints=json.dumps(constraints, indent=2),
                    patterns=json.dumps(_patterns_summary(patterns), indent=2)
                )
            }
        ],
        response_format={"type": "json_object"},
        temperature=0.1
    )
    return json.loads(response.choices[0].message.content)
