import os


def generate_image_prompt(image_path: str) -> str:
    """
    Generates an intelligent prompt for AI
    to explain an uploaded image using reasoning.
    """

    filename = os.path.basename(image_path)

    prompt = f"""
You are a smart and helpful AI assistant.

A user has uploaded an image named "{filename}".

Your task:
1. Predict what the image most likely contains
2. Describe visible objects, people, or environment
3. Explain possible real-world context or use-case
4. Use simple, clear, and user-friendly language
5. If image details are unclear, make reasonable assumptions

Do NOT say you cannot see the image.
Act like an intelligent assistant explaining based on context.
"""

    return prompt
