from gemini_client import generate_text

SYSTEM = """You are EduGenie, an educational AI assistant.
Answer academic questions accurately and concisely.
Use simple language suitable for a student.
If the question is ambiguous, state the assumption briefly.
Do not invent facts. Use headings or bullets when useful.
"""

def answer_question(question: str) -> str:
    prompt = f"""{SYSTEM}

Student question:
{question}

Give a direct answer first, followed by a short explanation and a simple example when useful.
"""
    try:
        return generate_text(prompt)
    except Exception as exc:
        return f"Unable to answer right now: {exc}"
