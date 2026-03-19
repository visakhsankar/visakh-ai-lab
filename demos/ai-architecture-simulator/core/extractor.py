import json
import os
from openai import OpenAI

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

EXTRACTION_PROMPT = """You are an enterprise AI architect. A client has described their use case.
Extract the key constraints and requirements in structured JSON format.

Client description: {description}

Return a JSON object with EXACTLY these fields:
{{
  "latency_sensitivity": "low or medium or high",
  "budget": "low or medium or high",
  "data_sensitivity": "low or medium or high",
  "team_capability": "beginner or intermediate or advanced or expert",
  "use_case_type": "short description e.g. document Q&A, customer support chatbot, enterprise search",
  "data_sources": ["list of data sources mentioned"],
  "scale": "small or medium or large or enterprise",
  "domain": "industry domain e.g. healthcare, finance, legal, general",
  "key_requirements": ["top 3-5 specific requirements extracted"],
  "constraints_summary": "one sentence summary of the core challenge"
}}

Rules:
- latency_sensitivity: high = real-time/fast required, low = batch/async ok
- budget: low = startup/tight, high = enterprise/no constraint
- data_sensitivity: high = HIPAA/GDPR/can't leave org, low = public data ok
- team_capability: based on ML/AI experience mentioned

Return ONLY valid JSON, no other text.
"""


def extract_constraints(description: str) -> dict:
    """Extract structured constraints from a natural language use case description."""
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": EXTRACTION_PROMPT.format(description=description)}
        ],
        response_format={"type": "json_object"},
        temperature=0.1
    )
    return json.loads(response.choices[0].message.content)
