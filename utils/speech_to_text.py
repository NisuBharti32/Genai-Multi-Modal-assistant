# utils/speech_to_text.py

def voice_to_text(text_from_browser=None):
    """
    Browser se aaya hua speech-text return karega.
    Agar empty hua to safe default dega.
    """
    if text_from_browser and text_from_browser.strip():
        return text_from_browser.strip()
    return ""
