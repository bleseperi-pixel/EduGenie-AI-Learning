from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

from qna import answer_question
from explanation_module import explain_topic
from quiz_module import generate_quiz
from summary_module import summarize_text
from learning_path import get_learning_recommendations

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(title="EduGenie", version="1.0.0")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")


class TextRequest(BaseModel):
    text: str = Field(min_length=1, max_length=30000)


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
   return templates.TemplateResponse(request, "index.html")


@app.get("/health")
async def health():
    return {"status": "ok", "service": "EduGenie"}


@app.post("/qa")
async def qa(request: TextRequest):
    return {"result": answer_question(request.text)}


@app.post("/explain")
async def explain(request: TextRequest):
    return {"result": explain_topic(request.text)}


@app.post("/quiz")
async def quiz(request: TextRequest):
    return generate_quiz(request.text)


@app.post("/summarize")
async def summarize(request: TextRequest):
    return {"result": summarize_text(request.text)}


@app.post("/learn/recommendations")
async def learning_recommendations(request: TextRequest):
    return {"result": get_learning_recommendations(request.text)}
#changed
#finish

