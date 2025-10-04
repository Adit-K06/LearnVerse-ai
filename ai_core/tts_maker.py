import os
from gtts import gTTS
import pyttsx3
from .utils import ensure_dir

def make_tts_gtts(text, out_path, lang="en"):
    # Try gTTS first (requires internet)
    tts = gTTS(text=text, lang=lang, slow=False)
    tts.save(out_path)
    return out_path

def make_tts_pyttsx3(text, out_path):
    # Offline fallback (may sound robotic)
    engine = pyttsx3.init()
    # save to file (pyttsx3 supports saving as wav via driver on many setups)
    engine.save_to_file(text, out_path)
    engine.runAndWait()
    return out_path

def make_tts(text, out_path):
    ensure_dir(os.path.dirname(out_path) or ".")
    try:
        return make_tts_gtts(text, out_path)
    except Exception as e:
        print("gTTS failed, falling back to pyttsx3:", e)
        # ensure wav extension for pyttsx3
        if not out_path.lower().endswith(".wav"):
            out_path = os.path.splitext(out_path)[0] + ".wav"
        return make_tts_pyttsx3(text, out_path)
