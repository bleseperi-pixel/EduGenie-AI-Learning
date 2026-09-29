"""Question answering with Gemini."""
import gemini_client

SYSTEM = (
    "You are EduGenie, a friendly and accurate tutor for students. Answer the question "
    "clearly and concisely. Give the direct answer first, then a short supporting "
    "explanation if it helps. If you are unsure, say so instead of guessing."
)


def answer_question(question: str) -> str:
    return gemini_client.generate(question, system_instruction=SYSTEM, temperature=0.3)
