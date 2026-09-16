from flask import Flask, render_template, request
import os
import re

from dotenv import load_dotenv
from groq import Groq

import pytesseract
from PIL import Image
import cv2
from werkzeug.utils import secure_filename

from utils.image_reader import analyze_image

# Tesseract path
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

load_dotenv()
app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "uploads"
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "bmp", "tiff"}

# Current supported Groq text model for /ask and /voice only
# (llama-3.1-8b-instant is now Enterprise-only and returns 404 on this tier)
GROQ_MODEL = "openai/gpt-oss-120b"

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

#   EMOTION DETECTOR (rule-based, 5 categories)
def detect_emotion(text):
    text = text.lower()

    angry_words = [
        "angry", "frustrated", "frustrating", "annoyed", "annoying",
        "irritated", "pissed", "hate this", "so bad", "worst",
        "gussa", "bakwas", "galat", "chid"
    ]

    confused_words = [
        "confused", "confusing", "confuse",
        "samajh nahi", "samajh nahi aa raha", "mujhe samajh nahi",
        "not clear", "clear nahi",
        "don't understand", "dont understand", "do not understand",
        "no idea", "lost", "not getting", "not able to understand",
        "what does this mean", "how does this work", "what are you saying"
    ]

    sad_words = [
        "sad", "upset", "unhappy", "down", "depressed", "hopeless",
        "udaas", "dukhi", "mann nahi", "not feeling good", "low today",
        "feeling low"
    ]

    happy_words = [
        "happy", "great", "awesome", "amazing", "excited", "love this",
        "wonderful", "fantastic", "khush", "mast", "badhiya"
    ]

    # Order matters: check the more specific / less ambiguous sets first
    for w in angry_words:
        if w in text:
            return "angry"
    for w in confused_words:
        if w in text:
            return "confused"
    for w in sad_words:
        if w in text:
            return "sad"
    for w in happy_words:
        if w in text:
            return "happy"

    return "neutral"

#   OCR TEXT
def clean_extracted_text(text):
    lines = text.split("\n")
    filtered = []

    for line in lines:
        line = line.strip()

        if len(line) < 3:
            continue

        # remove garbage like numbers only
        if re.match(r'^[\d\.\-/() ]+$', line):
            continue

        filtered.append(line)

    return "\n".join(filtered)


def fix_numbered_lines(text):
    text = re.sub(r'\s*(\d+\.)', r'\n\1', text)
    return text.strip()


@app.route("/")
def home():
    return render_template("index.html")

# -TEXT INPUT
@app.route("/ask", methods=["POST"])
def ask_ai():
    user_text = request.form.get("text", "")
    emotion = detect_emotion(user_text)
    reply = generate_response(user_text, emotion)

    return render_template("index.html", reply=reply, emotion=emotion)

#   VOICE INPUT
@app.route("/voice", methods=["GET"])
def voice():
    text = request.args.get("text", "")

    if not text:
        return render_template(
            "index.html",
            reply="No voice input received.",
            emotion="neutral"
        )

    emotion = detect_emotion(text)
    reply = generate_response(text, emotion)

    return render_template(
        "index.html",
        reply=reply,
        emotion=emotion
    )

#  IMAGE INPUT
@app.route("/image", methods=["POST"])
def image():
    file = request.files.get("image")

    if not file or file.filename == "":
        return render_template(
            "index.html",
            reply="No image uploaded.",
            emotion="neutral"
        )

    filename = secure_filename(file.filename)
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        return render_template(
            "index.html",
            reply="Unsupported file type. Please upload a PNG, JPG, JPEG, BMP, or TIFF image.",
            emotion="neutral"
        )

    image_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(image_path)

    #  OCR (kept as supporting context for the vision model — no longer
    #  the only thing sent to the LLM, and no longer a hard blocker if it fails)
    extracted_text = ""
    img = cv2.imread(image_path)
    if img is not None:
        try:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            gray = cv2.threshold(
                gray, 0, 255,
                cv2.THRESH_BINARY + cv2.THRESH_OTSU
            )[1]
            custom_config = r'--oem 3 --psm 6'
            raw_text = pytesseract.image_to_string(gray, config=custom_config).strip()
            extracted_text = clean_extracted_text(raw_text)
        except Exception:
            extracted_text = ""

    #  VISION MODEL — receives the actual image + OCR text as a hint
    reply = analyze_image(image_path, ocr_text=extracted_text)

    return render_template(
        "index.html",
        reply=reply,
        emotion="neutral"
    )

# ---------- EMOTION-ADAPTIVE RESPONSE ----------
EMOTION_SYSTEM_PROMPTS = {
    "angry": """
You are a calm, empathetic AI assistant.
The user seems frustrated or angry.

RULES:
- Acknowledge their frustration briefly, without over-apologizing
- Stay calm and reassuring
- Get to a clear, useful answer quickly
- Answer in ONE short paragraph, no numbered points
""",
    "confused": """
You are a patient teacher.
The user seems confused.

STRICT RULES:
- Answer step by step
- Use numbered points (1, 2, 3...)
- Each step = one clear, simple sentence
- No paragraph
""",
    "sad": """
You are a supportive, gentle AI assistant.
The user seems a bit down or discouraged.

RULES:
- Keep the tone warm and encouraging, without being dismissive
- Still give a clear, useful, correct answer
- Answer in ONE short, kind paragraph, no numbered points
""",
    "happy": """
You are a friendly, upbeat AI assistant.
The user seems happy or excited.

RULES:
- Match their positive energy briefly
- Keep the answer clear and useful
- Answer in ONE short paragraph, no numbered points
""",
    "neutral": """
You are a helpful AI assistant.

RULES:
- Answer in ONE short paragraph
- Do NOT use numbered points
- Keep it simple and natural
""",
}


def generate_response(text, emotion):
    if not text:
        return "Please ask something."

    system_prompt = EMOTION_SYSTEM_PROMPTS.get(emotion, EMOTION_SYSTEM_PROMPTS["neutral"])
    temperature = 0.2 if emotion == "confused" else 0.6

    try:
        res = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text}
            ],
            temperature=temperature
        )
        reply = res.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {e}"

    if emotion == "confused":
        reply = fix_numbered_lines(reply)

    return reply

#  RUN
if __name__ == "__main__":
    app.run(debug=True)