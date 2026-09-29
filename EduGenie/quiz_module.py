import json
import re
from gemini_client import generate_text

def clean_json_block(text: str) -> str:
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*```$", "", text)
    return text.strip()


def generate_quiz(source: str) -> dict:
    prompt = f"""
Create exactly 3 multiple-choice questions from the material below.

Return ONLY valid JSON. No markdown and no extra text.
The JSON must have this exact shape:
{{
  "questions": [
    {{
      "question": "string",
      "options": ["A", "B", "C", "D"],
      "answer": "A"
    }}
  ]
}}

Rules:
- Exactly 3 questions.
- Exactly 4 options per question.
- "answer" must be exactly one of A, B, C, D.
- Questions must be answerable from the supplied material.
- Make distractors plausible.
- Do not repeat the same question.

MATERIAL:
{source}
"""
    try:
        raw = clean_json_block(generate_text(prompt))
        data = json.loads(raw)
        questions = data.get("questions", [])
        if len(questions) != 3:
            raise ValueError("Gemini did not return exactly 3 questions.")
        for q in questions:
            if not isinstance(q.get("options"), list) or len(q["options"]) != 4:
                raise ValueError("Each question must have 4 options.")
            if q.get("answer") not in {"A", "B", "C", "D"}:
                raise ValueError("Invalid answer key.")
        return {"questions": questions}
    except Exception as exc:
        return {"questions": [], "error": str(exc)}
