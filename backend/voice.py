from gtts import gTTS
import os
import hashlib
from datetime import datetime

AUDIO_DIR = "../audio"
os.makedirs(AUDIO_DIR, exist_ok=True)

def generate_voice_message(recommendation_text, language="odia"):
    """
    Generate voice message in Odia or English
    Uses Google Text-to-Speech
    
    For production: Use better TTS like Coqui, or Indic TTS
    """
    
    # Language mapping
    lang_codes = {
        "odia": "or",  # Odia (if available, else falls back)
        "english": "en",
        "hindi": "hi"
    }
    
    lang_code = lang_codes.get(language, "en")
    
    # Generate unique filename
    text_hash = hashlib.md5(recommendation_text.encode()).hexdigest()[:8]
    filename = f"advice_{text_hash}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3"
    filepath = os.path.join(AUDIO_DIR, filename)
    
    try:
        # For Odia, simplify message (gTTS Odia support limited)
        if language == "odia":
            # Transliterate or simplify (in production, use proper Indic TTS)
            simplified_text = simplify_for_odia(recommendation_text)
        else:
            simplified_text = recommendation_text
        
        # Generate audio
        tts = gTTS(text=simplified_text, lang=lang_code, slow=False)
        tts.save(filepath)
        
        return f"/audio/{filename}"
    
    except Exception as e:
        print(f"Voice generation error: {e}")
        return None

def simplify_for_odia(text):
    """
    Simplify English text for Odia TTS
    In production: Translate properly using IndicTrans or similar
    """
    # For demo: Use simple English with key Odia terms
    simplified = text.replace("URGENT", "ଜରୁରୀ")
    simplified = simplified.replace("Paddy", "ଧାନ")
    return simplified


# PRODUCTION: Use Indic TTS or Coqui
"""
from TTS.api import TTS

tts_model = TTS("tts_models/multilingual/multi-dataset/your_tts")

def generate_voice_odia_production(text):
    filepath = f"audio/odia_{datetime.now().timestamp()}.wav"
    tts_model.tts_to_file(
        text=text,
        file_path=filepath,
        speaker="odia_female",  # Assuming model supports Odia
        language="or"
    )
    return filepath
"""
