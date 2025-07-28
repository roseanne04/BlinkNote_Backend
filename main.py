# backend/main.py

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from backend.cohere_summarizer import generate_structured_summary

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For dev only. Restrict in production.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request model
class TranscriptRequest(BaseModel):
    transcript: str

# Response model
class SummaryResponse(BaseModel):
    summary: str
    action_items: list[str]
    deadlines: list[str]
    assignees: list[str]
    key_decisions: list[str]
    follow_ups: list[str]
    priority_tasks: list[str]

@app.post("/summarize", response_model=SummaryResponse)
async def summarize_transcript(req: TranscriptRequest):
    structured_output = generate_structured_summary(req.transcript)
    return structured_output
