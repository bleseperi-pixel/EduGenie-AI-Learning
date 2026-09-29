"""Offline tests: the Gemini call is replaced with a fake, so no API key or internet is needed."""
import pytest
from fastapi.testclient import TestClient

import explanation_module
import gemini_client
from main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def _env(monkeypatch):
    monkeypatch.setenv("EXPLAIN_BACKEND", "gemini")


def fake_gemini(monkeypatch, reply):
    monkeypatch.setattr(gemini_client, "generate", lambda prompt, **kwargs: reply)


def test_home_page_renders():
    r = client.get("/")
    assert r.status_code == 200 and "EduGenie" in r.text


def test_static_files_served():
    assert client.get("/static/style.css").status_code == 200
    assert client.get("/static/app.js").status_code == 200


def test_health():
    body = client.get("/health").json()
    assert body["status"] == "ok" and "gemini_model" in body


def test_qa(monkeypatch):
    fake_gemini(monkeypatch, "The Pacific Ocean.")
    r = client.post("/qa", json={"question": "Which is the largest ocean?"})
    assert r.status_code == 200 and r.json()["answer"] == "The Pacific Ocean."


def test_qa_requires_input():
    r = client.post("/qa", json={"question": "   "})
    assert r.status_code == 400 and "error" in r.json()


def test_explain_with_gemini_backend(monkeypatch):
    fake_gemini(monkeypatch, "Plants make food from sunlight.")
    body = client.post("/explain", json={"topic": "Photosynthesis"}).json()
    assert body["engine"] == "Gemini" and "sunlight" in body["explanation"]


def test_explain_falls_back_to_gemini_when_local_model_fails(monkeypatch):
    monkeypatch.setenv("EXPLAIN_BACKEND", "local")

    def boom(topic):
        raise OSError("model not downloaded")

    monkeypatch.setattr(explanation_module, "_explain_local", boom)
    fake_gemini(monkeypatch, "Fallback explanation.")
    body = client.post("/explain", json={"topic": "Gravity"}).json()
    assert body["engine"] == "Gemini"


def test_explain_uses_local_model_when_available(monkeypatch):
    monkeypatch.setenv("EXPLAIN_BACKEND", "local")
    monkeypatch.setattr(explanation_module, "_explain_local", lambda topic: "Local text.")
    body = client.post("/explain", json={"topic": "Gravity"}).json()
    assert body["engine"].startswith("LaMini") and body["explanation"] == "Local text."


QUIZ_JSON = """```json
[
 {"question": "What is 2+2?", "options": ["A) 3", "B) 4", "C) 5", "D) 6"], "answer": "B"},
 {"question": "Capital of France?", "options": ["Paris", "Rome", "Madrid", "Berlin"], "answer": "paris"},
 {"question": "Largest planet?", "options": ["Earth", "Mars", "Jupiter", "Venus"], "answer": "Jupiter"}
]
```"""


def test_quiz_parses_fenced_json_and_normalizes_answers(monkeypatch):
    fake_gemini(monkeypatch, QUIZ_JSON)
    quiz = client.post("/quiz", json={"text": "General knowledge"}).json()["quiz"]
    assert len(quiz) == 3
    assert quiz[0]["options"] == ["3", "4", "5", "6"] and quiz[0]["answer"] == "4"
    assert quiz[1]["answer"] == "Paris"


def test_quiz_bad_output_returns_error(monkeypatch):
    fake_gemini(monkeypatch, "Sorry, I cannot do that")
    r = client.post("/quiz", json={"text": "Anything"})
    assert r.status_code == 502 and "error" in r.json()


def test_summarize(monkeypatch):
    fake_gemini(monkeypatch, "Short summary.")
    assert client.post("/summarize", json={"text": "Long text " * 50}).json()["summary"] == "Short summary."


def test_learning_recommendations(monkeypatch):
    fake_gemini(monkeypatch, "**I. Beginner Level**")
    body = client.get("/learn/recommendations", params={"topic": "SQL"}).json()
    assert body["topic"] == "SQL" and "Beginner" in body["recommendation"]


def test_learning_recommendations_requires_topic():
    r = client.get("/learn/recommendations")
    assert r.status_code == 422 and "error" in r.json()


def test_missing_api_key_gives_clear_error(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "")
    monkeypatch.setenv("GOOGLE_API_KEY", "")
    monkeypatch.setattr(gemini_client, "_client", None)
    r = client.post("/qa", json={"question": "Hello?"})
    assert r.status_code == 503 and "GEMINI_API_KEY" in r.json()["error"]


def test_input_too_long_rejected():
    r = client.post("/summarize", json={"text": "x" * 20_001})
    assert r.status_code == 413
