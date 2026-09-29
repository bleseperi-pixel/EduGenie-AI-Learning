"""Shared Google Gemini helper used by the Q&A, quiz, summary and learning-path modules."""
import os
from typing import Optional

from dotenv import load_dotenv

load_dotenv()

DEFAULT_MODEL = "gemini-2.5-flash"


class ApiError(Exception):
    """An error that should be returned to the client as {"error": message}."""

    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class GeminiError(ApiError):
    """Raised when the Gemini API is misconfigured, fails, or returns unusable output."""

    def __init__(self, message: str, status_code: int = 502):
        super().__init__(message, status_code)


_client = None


def get_model_name() -> str:
    return os.getenv("GEMINI_MODEL", DEFAULT_MODEL).strip() or DEFAULT_MODEL


def _api_key() -> Optional[str]:
    key = (os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or "").strip()
    if not key or key.startswith("your_"):
        return None
    return key


def has_api_key() -> bool:
    return _api_key() is not None


def _get_client():
    global _client
    if _client is None:
        key = _api_key()
        if not key:
            raise GeminiError(
                "GEMINI_API_KEY is not set. Copy .env.example to .env, add your key "
                "from Google AI Studio, then restart the server.",
                status_code=503,
            )
        from google import genai  # imported lazily so the app still starts without a key

        _client = genai.Client(api_key=key)
    return _client


def generate(
    prompt: str,
    *,
    system_instruction: Optional[str] = None,
    json_output: bool = False,
    temperature: float = 0.4,
) -> str:
    """Send one prompt to Gemini and return the response text."""
    client = _get_client()
    from google.genai import types

    config_kwargs = {"temperature": temperature}
    if system_instruction:
        config_kwargs["system_instruction"] = system_instruction
    if json_output:
        config_kwargs["response_mime_type"] = "application/json"

    try:
        response = client.models.generate_content(
            model=get_model_name(),
            contents=prompt,
            config=types.GenerateContentConfig(**config_kwargs),
        )
    except Exception as exc:  # network, quota, invalid key, unknown model, ...
        raise GeminiError(f"Gemini request failed: {exc}") from exc

    text = (getattr(response, "text", None) or "").strip()
    if not text:
        raise GeminiError(
            "Gemini returned an empty response (it may have been blocked by a safety "
            "filter). Try rephrasing your input."
        )
    return text
