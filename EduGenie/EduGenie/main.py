"""EduGenie - FastAPI application.

Run with:  uvicorn main:app --reload
"""
import logging
import os
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

import gemini_client
from explanation_module import explain_topic_detailed
from gemini_client import ApiError
from learning_path import get_learning_recommendations
from qna import answer_question
from quiz_module import generate_quiz
from summary_module import summarize_text

logging.basicConfig(level=logging.INFO)

BASE_DIR = Path(__file__).resolve().parent
MAX_INPUT_CHARS = 20_000

app = FastAPI(title="EduGenie", description="Google Gemini powered learning assistant", version="1.0.0")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


class TextPayload(BaseModel):
    """Every POST endpoint accepts JSON; each one reads the field(s) it needs."""

    text: Optional[str] = None
    question: Optional[str] = None
    topic: Optional[str] = None


def pick_text(payload: TextPayload, *fields: str, what: str) -> str:
    for field in fields:
        value = (getattr(payload, field, None) or "").strip()
        if value:
            if len(value) > MAX_INPUT_CHARS:
                raise ApiError(f"Input is too long (max {MAX_INPUT_CHARS:,} characters).", 413)
            return value
    raise ApiError(f"Please provide {what}.", 400)


# ---------- error handling: always respond with {"error": "..."} ----------
@app.exception_handler(ApiError)
async def api_error_handler(_: Request, exc: ApiError):
    return JSONResponse({"error": exc.message}, status_code=exc.status_code)


@app.exception_handler(RequestValidationError)
async def validation_error_handler(_: Request, exc: RequestValidationError):
    return JSONResponse({"error": "Invalid request: a required field is missing or malformed."}, status_code=422)


# ---------- pages ----------
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(request, "index.html")


@app.get("/health")
def health():
    return {
        "status": "ok",
        "gemini_key_configured": gemini_client.has_api_key(),
        "gemini_model": gemini_client.get_model_name(),
        "explain_backend": os.getenv("EXPLAIN_BACKEND", "local"),
    }


# ---------- API endpoints (plain `def` => FastAPI runs the blocking AI calls in a thread pool) ----------
@app.post("/qa")
def qa_api(payload: TextPayload):
    question = pick_text(payload, "question", "text", what="a question")
    return {"question": question, "answer": answer_question(question)}


@app.post("/explain")
def explain_api(payload: TextPayload):
    topic = pick_text(payload, "topic", "text", what="a topic to explain")
    explanation, engine = explain_topic_detailed(topic)
    return {"topic": topic, "explanation": explanation, "engine": engine}


@app.post("/quiz")
def quiz_api(payload: TextPayload):
    text = pick_text(payload, "text", "topic", what="a topic or text for the quiz")
    return {"quiz": generate_quiz(text)}


@app.post("/summarize")
def summarize_api(payload: TextPayload):
    text = pick_text(payload, "text", what="text to summarize")
    return {"summary": summarize_text(text)}


@app.get("/learn/recommendations")
def learning_recommendation_api(topic: str = Query(..., min_length=2, max_length=200)):
    topic = topic.strip()
    return {"topic": topic, "recommendation": get_learning_recommendations(topic)}
