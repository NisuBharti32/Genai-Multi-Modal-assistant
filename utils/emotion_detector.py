def detect_emotion(text):
    text = text.lower()

    confused_words = ["samajh nahi", "confused", "kaise", "kyu", "explain"]
    angry_words = ["galat", "kya yaar", "bakwas", "nonsense"]

    for word in confused_words:
        if word in text:
            return "confused"

    for word in angry_words:
        if word in text:
            return "angry"

    return "neutral"
