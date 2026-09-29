import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()

GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.8-flash"
).strip()

GEMINI_FALLBACK_MODEL = os.getenv(
    "GEMINI_FALLBACK_MODEL",
    "gemini-3.7-flash"
).strip()

ENABLE_LOCAL_EXPLAINER = os.getenv(
    "ENABLE_LOCAL_EXPLAINER",
    "false"
).lower() == "true"

LOCAL_MODEL = os.getenv(
    "LOCAL_MODEL",
    "MBZUAI/LaMini-Flan-T5-783M"
).strip()