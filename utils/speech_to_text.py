# utils/speech_to_text.py

def voice_to_text(text_from_browser=None):
    """
     Returns the speech text received from the browser.
    If the input is empty, it returns a safe default value.
    """
    if text_from_browser and text_from_browser.strip():
        return text_from_browser.strip()
    return ""
