import os
import json
from typing import List
from huggingface_hub import InferenceClient
from models import TaskItem

HF_API_KEY = os.getenv("HF_API_KEY")
client = InferenceClient(model="tiiuae/falcon-7b-instruct", token=HF_API_KEY)

def extract_action_items(summary: str) -> List[TaskItem]:
    prompt = f"""
From the following meeting summary, extract all task assignments as structured JSON.

Each task should include:
- task_name: Brief name of the task
- assignee: Person assigned
- deadline: Deadline if mentioned, else "None"

Meeting Summary:
\"\"\"
{summary}
\"\"\"

Return format:
[
  {{
    "task_name": "Create project plan",
    "assignee": "Alice",
    "deadline": "2025-08-01"
  }},
  ...
]
"""

    try:
        response = client.text_generation(prompt, max_new_tokens=512, temperature=0.3, do_sample=False)
        print("HF response:", response)

        task_list = json.loads(response)
        return [TaskItem(**task) for task in task_list]
    except Exception as e:
        print("Error extracting task items from HF:", e)
        return []