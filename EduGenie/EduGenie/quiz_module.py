"""Quiz generation: 3 multiple-choice questions (4 options each) from a topic or passage."""
import json
import re

import gemini_client
from gemini_client import GeminiError

SYSTEM = "You are a teacher who writes fair, accurate multiple-choice quizzes."

PROMPT = """Create exactly 3 multiple-choice questions based on the topic or passage below.
Each question must have exactly 4 options with plausible wrong answers and exactly one correct answer.

Return ONLY valid JSON (no markdown, no commentary) in this shape:
[
  {{"question": "...", "options": ["option 1", "option 2", "option 3", "option 4"], "answer": "the exact text of the correct option"}}
]

Topic or passage:
{text}"""

_LABEL = re.compile(r"^\(?[A-Da-d][\).:\-]\s+")


def clean_json_block(raw: str) -> str:
    """Strip Markdown code fences (```json ... ```) that models sometimes add."""
    cleaned = raw.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    return cleaned.strip()


def _resolve_answer(answer: str, options: list) -> str:
    """Map the model's 'answer' field to one of the four option strings."""
    answer = answer.strip()
    if re.fullmatch(r"\(?[A-Da-d]\)?[.:]?", answer):  # just a letter, e.g. "B" or "B)"
        return options["ABCD".index(answer.strip("().:").upper())]
    stripped = _LABEL.sub("", answer).strip()
    for candidate in (answer, stripped):
        for option in options:
            if candidate.lower() == option.lower():
                return option
    raise ValueError(f"answer {answer!r} does not match any option")


def _normalize(data) -> list:
    if isinstance(data, dict):
        data = data.get("quiz") or data.get("questions") or []
    if not isinstance(data, list) or not data:
        raise ValueError("expected a non-empty list of questions")

    quiz = []
    for i, item in enumerate(data[:3], start=1):
        try:
            question = str(item["question"]).strip()
            options = [_LABEL.sub("", str(o)).strip() for o in item["options"]]
            if not question or len(options) != 4 or not all(options):
                raise ValueError("needs a question and exactly 4 options")
            correct = _resolve_answer(str(item["answer"]), options)
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError(f"question {i} is malformed: {exc}") from exc
        quiz.append({"question": question, "options": options, "answer": correct})
    return quiz


def generate_quiz(text: str) -> list:
    raw = gemini_client.generate(
        PROMPT.format(text=text),
        system_instruction=SYSTEM,
        json_output=True,
        temperature=0.6,
    )
    try:
        return _normalize(json.loads(clean_json_block(raw)))
    except (json.JSONDecodeError, ValueError) as exc:
        raise GeminiError(
            f"Could not parse the quiz returned by Gemini ({exc}). Please try again."
        ) from exc
