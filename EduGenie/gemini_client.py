import time
from google import genai

from config import (
    GEMINI_API_KEY,
    GEMINI_MODEL,
    GEMINI_FALLBACK_MODEL,
)

_client = None


def get_client():
    global _client

    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY is missing.")

    if _client is None:
        _client = genai.Client(api_key=GEMINI_API_KEY)

    return _client


def call_model(model, prompt):
    response = get_client().models.generate_content(
        model=model,
        contents=prompt,
    )

    text = getattr(response, "text", None)

    if not text:
        raise RuntimeError("Model returned an empty response.")

    return text.strip()


def generate_text(prompt: str) -> str:

    # Try primary model
    for attempt in range(2):
        try:
            return call_model(GEMINI_MODEL, prompt)

        except Exception as e:
            error = str(e)

            if "503" not in error and "UNAVAILABLE" not in error:
                raise RuntimeError(f"Gemini request failed: {error}")

            if attempt == 0:
                time.sleep(2)

    # Try fallback model
    try:
        print(f"Primary model unavailable. Trying {GEMINI_FALLBACK_MODEL}...")
        return call_model(GEMINI_FALLBACK_MODEL, prompt)

    except Exception as e:
        raise RuntimeError(
            "Both Gemini models are temporarily unavailable. "
            "Please try again shortly."
        )