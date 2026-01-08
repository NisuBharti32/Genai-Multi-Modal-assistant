from flask import Flask, render_template, request
import os
from dotenv import load_dotenv
from openai import OpenAI
from werkzeug.utils import secure_filename

from utils.speech_to_text import voice_to_text

# ---------- INIT ----------
load_dotenv()

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

# ✅ GROQ CLIENT (OpenAI-compatible)
client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

# ---------- STRONG EMOTION DETECTOR ----------
def detect_emotion(text):
    text = text.lower()

    angry_words = [
        "angry", "frustrated", "irritated", "annoyed",
        "nonsense", "stupid", "worst", "useless",
        "doesn't make sense", "fed up", "hate"
    ]

    confused_words = [
        "confused", "not clear", "don't understand",
        "what is this", "how", "why"
    ]

    happy_words = [
        "happy", "excited", "great", "awesome",
        "love", "amazing"
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
    audio = request.args.get("text", "")
    text = voice_to_text(audio)

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
        return render_template("index.html", reply="No image uploaded")

    path = os.path.join(
        app.config['UPLOAD_FOLDER'],
        secure_filename(file.filename)
    )
    file.save(path)

    prompt = f"Explain what is happening in this image: {file.filename}"
    emotion = "neutral"

    reply = get_ai_response(prompt, emotion)

    return render_template(
        "index.html",
        reply=reply,
        emotion=emotion
    )

# ---------- AI RESPONSE ----------
def get_ai_response(text, emotion):
    if not text:
        return "Please ask something."

    # 🎯 Emotion only changes TONE
    if emotion == "angry":
        tone = (
            "User is frustrated. Respond calmly, politely, "
            "reassure them and give a clear correct answer."
        )
    elif emotion == "confused":
        tone = (
            "User is confused. Explain step by step in simple language "
            "with a small example."
        )
    elif emotion == "happy":
        tone = (
            "User is happy. Respond in a friendly and encouraging tone."
        )
    else:
        tone = "Respond in a clear and helpful tone."

    final_prompt = f"""
{tone}

User question:
{text}

IMPORTANT:
- Focus on answering the question.
- Do NOT explain the emotion.
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "user", "content": final_prompt}
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
