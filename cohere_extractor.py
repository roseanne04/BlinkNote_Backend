import cohere
import os
import json
from typing import List, Dict
from dotenv import load_dotenv

# Load .env variables
load_dotenv()

# Check if API key is loaded
api_key = os.getenv("COHERE_API_KEY")
if not api_key:
    raise ValueError("COHERE_API_KEY not found in environment variables")

co = cohere.Client(api_key)

def extract_action_items(summary: str) -> List[Dict]:
    prompt = f"""
You are an intelligent meeting assistant. From the following meeting summary, extract structured task assignments in JSON format.

For each task, extract:
- task (what to do)
- assignee (person responsible)
- deadline (due date, if any)
- priority (high, medium, low — inferred from urgency/tone)

Respond in this exact JSON format:
[
  {{
    "task": "task description",
    "assignee": "name",
    "deadline": "YYYY-MM-DD" or "None",
    "priority": "High" | "Medium" | "Low"
  }},
  ...
]

Meeting summary:
\"\"\"{summary}\"\"\"
"""

    try:
        response = co.generate(
            model="command-r-plus",
            prompt=prompt,
            max_tokens=500,
            temperature=0.5,
        )

        output = response.generations[0].text.strip()

        # Clean and parse the JSON safely
        json_start = output.find("[")
        json_end = output.rfind("]") + 1
        if json_start == -1 or json_end == -1:
            print("No JSON found in output.")
            return []

        extracted = json.loads(output[json_start:json_end])
        return extracted

    except Exception as e:
        print("Cohere extraction failed:", e)
        return []
