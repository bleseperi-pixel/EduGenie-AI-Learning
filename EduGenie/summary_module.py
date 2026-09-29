from gemini_client import generate_text

def summarize_text(text: str) -> str:
    prompt = f"""
Summarize the following educational passage for quick revision.

Rules:
- Keep the important facts and relationships.
- Remove repetition and filler.
- Use simple English.
- Use 5-10 bullet points when appropriate.
- Do not add information that is not present in the passage.

PASSAGE:
{text}
"""
    try:
        return generate_text(prompt)
    except Exception as exc:
        return f"Unable to summarize right now: {exc}"
