from flask import Flask, render_template, request
import os
from dotenv import load_dotenv
from openai import OpenAI
from werkzeug.utils import secure_filename

# ---------- INIT ----------
load_dotenv()

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

# ---------- VOICE FLAG ----------
ENABLE_VOICE = os.getenv("ENABLE_VOICE", "false").lower() == "true"

if ENABLE_VOICE:
    try:
        from utils.speech_to_text import voice_to_text
    except Exception:
        ENABLE_VOICE = False

# ---------- IMAGE PROMPT ----------
from utils.image_reader import generate_image_prompt

# ---------- GROQ CLIENT ----------
client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

# ---------- EMOTION DETECTOR ----------
def detect_emotion(text):
    text = text.lower()

    angry_words = [
        "angry", "bakwas", "galat", "nonsense",
        "worst", "hate", "frustrated"
    ]
    confused_words = [
        "confused", "samajh", "kaise", "kyu",
        "how", "why", "not clear"
    ]
    happy_words = [
        "happy", "great", "awesome",
        "amazing", "love", "wow"
    ]

    for w in angry_words:
        if w in text:
            return "angry"

    for w in confused_words:
        if w in text:
            return "confused"

    for w in happy_words:
        if w in text:
            return "happy"

    return "neutral"

# ---------- HOME ----------
@app.route("/")
def home():
    return render_template("index.html")

# ---------- TEXT INPUT ----------
@app.route("/ask", methods=["POST"])
def ask_ai():
    text = request.form.get("text", "")

    emotion = detect_emotion(text)
    reply = get_ai_response(text, emotion)

    return render_template(
        "index.html",
        reply=reply,
        emotion=emotion
    )

# ---------- VOICE INPUT ----------
@app.route("/voice")
def voice():
    if not ENABLE_VOICE:
        return render_template(
            "index.html",
            reply="Voice input is disabled.",
            emotion="neutral"
        )

    text = request.args.get("text", "")
    text = voice_to_text(text)

    emotion = detect_emotion(text)
    reply = get_ai_response(text, emotion)

    return render_template(
        "index.html",
        reply=reply,
        emotion=emotion
    )

# ---------- IMAGE INPUT ----------
@app.route("/image", methods=["POST"])
def image():
    file = request.files.get("image")

    if not file:
        return render_template(
            "index.html",
            reply="No image uploaded",
            emotion="neutral"
        )

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    path = os.path.join(
        app.config['UPLOAD_FOLDER'],
        secure_filename(file.filename)
    )
    file.save(path)

    prompt = generate_image_prompt(path)
    reply = get_ai_response(prompt, "neutral")

    return render_template(
        "index.html",
        reply=reply,
        emotion="neutral"
    )

# ---------- AI RESPONSE (🔥 EMOTION-AWARE) ----------
def get_ai_response(text, emotion):
    if not text:
        return "Please ask something."

    if emotion == "angry":
        system_prompt = """
You are an empathetic AI assistant.
The user is angry or frustrated.

RULES:
- Be calm and polite
- Reassure the user
- Explain clearly
"""
    elif emotion == "confused":
        system_prompt = """
You are a patient teacher.
The user is confused.

RULES:
- Explain step by step
- Use simple language
- Give a small example
"""
    elif emotion == "happy":
        system_prompt = """
You are a friendly AI assistant.
The user is happy.

RULES:
- Be positive and encouraging
- Keep the tone warm
"""
    else:
        system_prompt = """
You are a helpful AI assistant.

RULES:
- Be neutral and informative
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text}
            ],
            temperature=0.6
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"Error: {e}"

# ---------- RUN ----------
if __name__ == "__main__":
    os.makedirs("uploads", exist_ok=True)
    app.run(debug=True)
