import os
import base64
from openai import OpenAI

# Same Groq OpenAI-compatible client pattern as app.py, kept local to this file
client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

# Current Groq vision-capable model (accepts text + image in one request)
VISION_MODEL = "qwen/qwen3.8-27b"

ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "gif"}


def _get_mime_type(image_path: str) -> str:
    ext = image_path.rsplit(".", 1)[-1].lower()
    if ext in ("jpg", "jpeg"):
        return "image/jpeg"
    if ext == "png":
        return "image/png"
    if ext == "webp":
        return "image/webp"
    if ext == "gif":
        return "image/gif"
    return ""  # unrecognized extension


def analyze_image(image_path: str, ocr_text: str = "") -> str:
    """
    Sends the ACTUAL image (base64-encoded) to a vision-capable model on
    Groq, along with any OCR-extracted text as supporting context, and
    returns the model's real, image-grounded answer.

    ocr_text is optional and only used as a cross-check (small/dense text
    or formulas can be misread by OCR) — the model is told to trust what
    it actually sees in the image over the OCR text if they disagree.
    """
    ext = image_path.rsplit(".", 1)[-1].lower() if "." in image_path else ""
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        return "That file type isn't supported for image analysis. Please upload a PNG, JPG, JPEG, WEBP, or GIF."

    try:
        with open(image_path, "rb") as f:
            image_bytes = f.read()
    except FileNotFoundError:
        return "Sorry, I couldn't find the uploaded image on the server."

    mime_type = _get_mime_type(image_path)
    base64_image = base64.b64encode(image_bytes).decode("utf-8")

    ocr_section = ""
    if ocr_text:
        ocr_section = f"""

For reference, an OCR tool extracted this text from the image (it can make
mistakes on small text, symbols, or formulas — trust what you actually see
in the image over this if they disagree):

{ocr_text}
"""

    instruction = f"""Look at this image and respond as follows:

1. If it contains an academic or programming question (math, DSA, OS,
   algorithm) or a table (e.g. a Banker's Algorithm table), solve it step
   by step using what you can actually see in the image, and give a clear
   final answer.
2. Otherwise, describe what is actually visible: key objects, people (if
   any), the setting, and any readable text.
3. If something is unclear or you're not confident about a detail, say so
   honestly instead of guessing.
{ocr_section}"""

    try:
        response = client.chat.completions.create(
            model=VISION_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": instruction},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:{mime_type};base64,{base64_image}"},
                        },
                    ],
                }
            ],
            temperature=0.3,
            max_completion_tokens=768,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error analyzing image: {e}"