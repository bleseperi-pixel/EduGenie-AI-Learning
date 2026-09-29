"""Personalized learning-path recommendations with Gemini."""
import gemini_client

SYSTEM = (
    "You are an experienced curriculum designer who builds clear, realistic study plans "
    "for self-learners."
)


def get_learning_recommendations(topic: str) -> str:
    prompt = f"""Create a structured learning path for the topic: "{topic}".

Use exactly these three sections, each with a bold heading:
**I. Beginner Level** (Estimated Time: ...)
**II. Intermediate Level** (Estimated Time: ...)
**III. Advanced Level** (Estimated Time: ...)

In every section include:
* **Key Topics:** a bullet list of concepts to learn
* **Resources:** specific videos, articles, books, courses or practice platforms

Finish with **Adaptive Learning Tips:** as 4-6 short bullet points.
Use '* ' for bullets and ** for bold. Keep it practical and encouraging."""
    return gemini_client.generate(prompt, system_instruction=SYSTEM, temperature=0.5)
