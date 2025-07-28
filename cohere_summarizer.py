import os
import cohere
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()
co = cohere.Client(os.getenv("COHERE_API_KEY"))

class StructuredSummary(BaseModel):
    summary: str

def generate_summary(transcript: str) -> StructuredSummary:
    prompt = f"""
Summarize the following meeting transcript in a clear and concise manner:

\"\"\"
{transcript}
\"\"\"

Return only the summary text.
"""
    response = co.generate(
        model="command-r-plus",
        prompt=prompt,
        max_tokens=400,
        temperature=0.4
    )

    summary = response.generations[0].text.strip()
    return StructuredSummary(summary=summary)
