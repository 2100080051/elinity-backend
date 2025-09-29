import os, tempfile, re, markdown
import speech_recognition as sr
from bs4 import BeautifulSoup
from elevenlabs import ElevenLabs, save

# Text cleaning for TTS
def sanitize_for_tts(text: str) -> str:
    try:
        html = markdown.markdown(text)
        text = BeautifulSoup(html, "html.parser").get_text(" ")
    except Exception:
        pass
    text = re.sub(r'[*`_~>#]+', '', text)
    text = re.sub(r'\b(comma|period|newline|tab)\b', '', text, flags=re.I)
    return re.sub(r'\s+', ' ', text).strip()

# Convert user voice to text
def transcribe_audio(audio_path):
    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(audio_path) as source:
            recognizer.adjust_for_ambient_noise(source)
            audio_data = recognizer.record(source)
            return recognizer.recognize_google(audio_data)
    except Exception as e:
        return {"error": str(e)}

# Convert text to speech
def text_to_speech(text):
    try:
        eleven_client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))
        clean_text = sanitize_for_tts(text)
        audio = eleven_client.generate(text=clean_text, model="eleven_turbo_v2")
        tmpfile = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        save(audio, tmpfile.name)
        return tmpfile.name
    except Exception as e:
        return {"error": str(e)}
