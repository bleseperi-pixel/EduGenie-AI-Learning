from gemini_client import generate_text

def get_learning_recommendations(topic: str) -> str:
    prompt = f"""
Create a personalized learning path for a student who wants to learn: {topic}

Structure the answer as:
1. Goal
2. Beginner foundations
3. Intermediate topics
4. Advanced topics
5. Suggested timeline
6. Practice projects
7. Resources to search for (videos, official documentation, books)
8. A simple weekly routine

Make the progression realistic and explain why each stage matters.
"""
    try:
        return generate_text(prompt)
    except Exception as exc:
        return f"Unable to create the learning path: {exc}"
