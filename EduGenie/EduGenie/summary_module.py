"""Summarization with Gemini."""
import gemini_client

SYSTEM = (
    "You summarize educational text for students. Keep every key fact and definition, "
    "remove repetition, and use simple language. Never add information that is not in "
    "the text."
)


def summarize_text(text: str) -> str:
    prompt = (
        "Summarize the passage below in a short paragraph, then list the 3-5 most "
        "important points as bullet points starting with '* '.\n\n"
        f"Passage:\n{text}"
    )
    return gemini_client.generate(prompt, system_instruction=SYSTEM, temperature=0.2)
