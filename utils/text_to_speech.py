from gtts import gTTS

def speak_text(text, language):
    lang_map = {
        "en": "en",
        "hi": "hi",
        "hinglish": "en"
    }

    tts = gTTS(text=text, lang=lang_map.get(language, "en"))
    tts.save("static/response.mp3")
