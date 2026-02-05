from flask import Flask, render_template, request
import os
import re
from dotenv import load_dotenv
from groq import Groq

# 🔹 OCR + CV imports
import pytesseract
from PIL import Image
import cv2

# 🔹 Tesseract path (Windows fix)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# ---------- INIT ----------
load_dotenv()
app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "uploads"
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# ---------- GROQ CLIENT ----------
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# ---------- EMOTION DETECTOR (FIXED) ----------
def detect_emotion(text):
    text = text.lower()

    # 🔥 ONLY strong confusion signals
    confused_words = [
        "i am confused",
        "samajh nahi",
        "samajh nahi aa raha",
        "mujhe samajh nahi",
        "not clear",
        "clear nahi",
        "confusing"
    ]

    for w in confused_words:
        if w in text:
            return "confused"

    return "neutral"

# ---------- STEP FORMAT FIX ----------
def fix_numbered_lines(text):
    text = re.sub(r'\s*(\d+\.)', r'\n\1', text)
    return text.strip()

# ---------- HOME ----------
@app.route("/")
def home():
    return render_template("index.html")

# ---------- TEXT INPUT ----------
@app.route("/ask", methods=["POST"])
def ask_ai():
    user_text = request.form.get("text", "")
    emotion = detect_emotion(user_text)

    if emotion == "confused":
        reply = confused_response(user_text)
    else:
        reply = normal_response(user_text)

    return render_template("index.html", reply=reply, emotion=emotion)

# ---------- VOICE INPUT (MIC FIX) ----------
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

    if emotion == "confused":
        reply = confused_response(text)
    else:
        reply = normal_response(text)

    return render_template(
        "index.html",
        reply=reply,
        emotion=emotion
    )

# ---------- IMAGE INPUT (UNCHANGED) ----------
@app.route("/image", methods=["POST"])
def image():
    file = request.files.get("image")

    if not file or file.filename == "":
        return render_template(
            "index.html",
            reply="No image uploaded.",
            emotion="neutral"
        )

    image_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(image_path)

    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.threshold(
        gray, 0, 255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )[1]

    custom_config = r'--oem 3 --psm 6'
    extracted_text = pytesseract.image_to_string(
        gray,
        config=custom_config
    ).strip()

    if not extracted_text:
        extracted_text = "Some text is present, but handwriting is unclear."

    prompt = f"""
The following text was extracted from an uploaded image (such as a medical prescription):

{extracted_text}

Explain the content clearly in simple language.
If medicines are mentioned, explain their usage in an easy way.
"""

    res = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "You explain extracted medical text clearly and responsibly."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )

    reply = res.choices[0].message.content.strip()

    return render_template(
        "index.html",
        reply=reply,
        emotion="neutral"
    )

# ---------- NORMAL TEXT RESPONSE (PARAGRAPH) ----------
def normal_response(text):
    system_prompt = """
You are a helpful AI assistant.

RULES:
- Answer in ONE short paragraph
- Do NOT use numbered points
- Do NOT explain step by step
- Keep language simple and natural
"""

    res = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text}
        ],
        temperature=0.6
    )
    return res.choices[0].message.content.strip()

# ---------- CONFUSED TEXT RESPONSE (STEP-BY-STEP) ----------
def confused_response(text):
    system_prompt = """
You are a patient teacher.

STRICT RULES:
- ALWAYS answer step by step
- Use ONLY numbered points (1, 2, 3...)
- Each point must be ONE complete sentence
- NO paragraphs
- NO extra text before or after steps
"""

    res = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text}
        ],
        temperature=0.2
    )

    return fix_numbered_lines(res.choices[0].message.content.strip())

# ---------- RUN ----------
if __name__ == "__main__":
    app.run(debug=True)
