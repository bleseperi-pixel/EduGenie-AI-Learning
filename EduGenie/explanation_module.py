from gemini_client import generate_text
from config import ENABLE_LOCAL_EXPLAINER, LOCAL_MODEL

_local_pipeline = None


def _local_explain(topic: str) -> str:
    global _local_pipeline
    try:
        from transformers import pipeline
    except ImportError:
        raise RuntimeError("Install transformers and torch to enable the local explainer.")

    if _local_pipeline is None:
        _local_pipeline = pipeline(
            "text2text-generation",
            model=LOCAL_MODEL,
            tokenizer=LOCAL_MODEL,
        )

    prompt = (
        "Explain this topic to a beginner in simple English. "
        "Use short paragraphs and one example. Topic: " + topic
    )
    result = _local_pipeline(prompt, max_new_tokens=220, do_sample=False)
    return result[0]["generated_text"].strip()


def explain_topic(topic: str) -> str:
    if ENABLE_LOCAL_EXPLAINER:
        try:
            return _local_explain(topic)
        except Exception:
            pass

    prompt = f"""
Explain the following topic like a patient teacher helping a beginner.

Topic: {topic}

Requirements:
- Start with a one-sentence definition.
- Explain the idea in simple English.
- Use a small real-world or academic example.
- Mention the key points the student should remember.
- Avoid unnecessary jargon.
"""
    try:
        return generate_text(prompt)
    except Exception as exc:
        return f"Unable to generate the explanation: {exc}"
