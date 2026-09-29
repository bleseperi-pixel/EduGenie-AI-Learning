"""Concept explanations.

Default engine: the local LaMini-Flan-T5-783M model (Hugging Face transformers + PyTorch).
The model is loaded lazily on the first request, so the server starts instantly. If the
local model can't be used (packages missing, download failed, out of memory) we fall back
to Gemini automatically. Set EXPLAIN_BACKEND=gemini in .env to skip the local model.
"""
import logging
import os
import threading
from typing import Tuple

import gemini_client

logger = logging.getLogger("edugenie.explain")

_lock = threading.Lock()
_tokenizer = None
_model = None
_device = "cpu"

GEMINI_SYSTEM = (
    "You explain concepts to school students in simple, clear language, using a short "
    "everyday analogy or example. Keep it under 150 words."
)


def _model_id() -> str:
    return os.getenv("EXPLAIN_MODEL_ID", "MBZUAI/LaMini-Flan-T5-783M")


def _load_local_model():
    global _tokenizer, _model, _device
    with _lock:
        if _model is None:
            import torch
            from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

            logger.info("Loading %s (first run downloads ~3 GB)...", _model_id())
            _tokenizer = AutoTokenizer.from_pretrained(_model_id())
            model = AutoModelForSeq2SeqLM.from_pretrained(_model_id())
            _device = "cuda" if torch.cuda.is_available() else "cpu"
            _model = model.to(_device).eval()
            logger.info("Local explanation model ready on %s.", _device)
    return _tokenizer, _model


def _explain_local(topic: str) -> str:
    import torch

    tokenizer, model = _load_local_model()
    prompt = f"Explain the concept of '{topic}' in a simple and clear way for a school student."
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512).to(_device)
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=150,
            temperature=0.7,
            top_k=50,
            top_p=0.95,
            do_sample=True,
        )
    text = tokenizer.decode(outputs[0], skip_special_tokens=True).strip()
    if not text:
        raise RuntimeError("local model returned empty text")
    return text


def _explain_gemini(topic: str) -> str:
    prompt = f"Explain the concept of '{topic}' in a simple and clear way for a school student."
    return gemini_client.generate(prompt, system_instruction=GEMINI_SYSTEM, temperature=0.5)


def explain_topic_detailed(topic: str) -> Tuple[str, str]:
    """Return (explanation, engine) where engine is 'LaMini-Flan-T5 (local)' or 'Gemini'."""
    if os.getenv("EXPLAIN_BACKEND", "local").strip().lower() != "gemini":
        try:
            return _explain_local(topic), "LaMini-Flan-T5 (local)"
        except Exception as exc:  # ImportError, OSError (download), RuntimeError (OOM), ...
            logger.warning("Local explanation model unavailable (%s); using Gemini.", exc)
    return _explain_gemini(topic), "Gemini"


def explain_topic(topic: str) -> str:
    return explain_topic_detailed(topic)[0]
