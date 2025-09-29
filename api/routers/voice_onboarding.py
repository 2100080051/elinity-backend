#!/usr/bin/env python3
import os
import json
import tempfile
import re, markdown
from bs4 import BeautifulSoup

import gradio as gr
import speech_recognition as sr
from elevenlabs import ElevenLabs, save
from dotenv import load_dotenv
import requests

# Import project components
from utils.gemini_genai import configure_genai, GeminiGenAIClient, transform_for_backend
from schemas.user import User

load_dotenv()

# ------------------------------
# Setup Clients
# ------------------------------
genai = configure_genai()
eleven_client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))

# ------------------------------
# Sanitizer for TTS
# ------------------------------
def sanitize_for_tts(text: str) -> str:
    try:
        html = markdown.markdown(text)
        text = BeautifulSoup(html, "html.parser").get_text(" ")
    except Exception:
        pass
    text = re.sub(r'[*`_~>#]+', '', text)
    text = re.sub(r'\b(comma|period|newline|tab)\b', '', text, flags=re.I)
    return re.sub(r'\s+', ' ', text).strip()

# ------------------------------
# Onboarding Prompt
# ------------------------------
ONBOARD_PROMPT = """You are ElinityAI, the user's intelligent, emotionally aware social connection guide.
Your task is to engage the user in a warm, insightful, and natural-feeling voice or text-based conversation
to deeply understand who they are — their values, goals, personality, communication style, emotional world,
and the kinds of people they are seeking in romantic, friendship, and collaboration contexts.

🎯 Goals of This Session
- Build emotional rapport and safety with the user.
- Extract detailed information to populate a deep user persona model.

🔁 General Instructions
- Use natural, friendly, emotionally attuned language.
- Ask one question at a time, then wait for response.
- Encourage storytelling over checkboxes.
"""

# ------------------------------
# Elinity Voice Onboarding Class
# ------------------------------
class ElinityVoiceOnboarding:
    def __init__(self, model_name="gemini-2.0-flash", system_prompt=ONBOARD_PROMPT):
        self.model = genai.GenerativeModel(model_name)
        self.conversation_history = []
        self.system_prompt = system_prompt
        self.genai_client = GeminiGenAIClient()
        self.recognizer = sr.Recognizer()
        self.eleven_client = eleven_client
        self.add_message("system", self.system_prompt)
        self.chat = self.model.start_chat(history=[])

    def add_message(self, role: str, content: str):
        self.conversation_history.append({"role": role, "content": content})

    def get_next_prompt(self, user_message: str) -> str:
        if not user_message:
            return "I didn't catch that. Could you please repeat?"
        self.add_message("user", user_message)
        response = self.chat.send_message(user_message)
        assistant_message = response.text
        self.add_message("assistant", assistant_message)
        return assistant_message

    def get_backend_token(self):
        """Fetch fresh token using USERNAME/PASSWORD from .env"""
        backend_url = os.getenv("BACKEND_URL", "http://localhost:8081")
        username = os.getenv("USERNAME")
        password = os.getenv("PASSWORD")
        try:
            resp = requests.post(
                f"{backend_url}/auth/token",
                data={"username": username, "password": password},
            )
            resp.raise_for_status()
            return resp.json().get("access_token")
        except Exception as e:
            print(f"[ERROR] Failed to fetch access token: {e}")
            return None

    def finalize_user_profile(self) -> dict:
        backend_url = os.getenv("BACKEND_URL", "http://localhost:8081")
        token = self.get_backend_token()
        headers = {"Authorization": f"Bearer {token}"} if token else {}

        # Step 1: Check backend profile
        try:
            resp = requests.get(f"{backend_url}/users/me", headers=headers)
            resp.raise_for_status()
            user_data = resp.json()

            # Debug log for clarity
            print("[DEBUG] Logged-in user response:", user_data)
            if "email" in user_data:
                print(f"[INFO] Current logged-in user: {user_data['email']}")
            elif user_data.get("personal_info", {}).get("email"):
                print(f"[INFO] Current logged-in user: {user_data['personal_info']['email']}")

            if (
                user_data.get("personal_info")
                or user_data.get("big_five_traits")
                or user_data.get("mbti_traits")
            ):
                print("[INFO] Profile already exists in backend. Returning it.")
                return user_data
        except Exception as e:
            print(f"[WARN] Could not fetch profile from backend: {e}")

        # Step 2: No profile → generate with Gemini
        profile_data = self.genai_client.generate_user_profile(self.conversation_history)
        if "error" in profile_data:
            return profile_data
        backend_payload = transform_for_backend(profile_data)

        # Step 3: Save into backend
        try:
            endpoints = {
                "personal_info": "personal-info",
                "big_five_traits": "big-five-traits",
                "mbti_traits": "mbti-traits",
                "psychology": "psychology",
                "interests_and_hobbies": "interests-and-hobbies",
                "values_beliefs_and_goals": "values-beliefs-and-goals",
                "favorites": "favorites",
                "relationship_preferences": "relationship-preferences",
                "friendship_preferences": "friendship-preferences",
                "collaboration_preferences": "collaboration-preferences",
                "personal_free_form": "personal-free-form",
                "intentions": "intentions",
                "ideal_characteristics": "ideal-characteristics",
                "aspiration_and_reflections": "aspiration-and-reflections",
            }
            for key, endpoint in endpoints.items():
                if backend_payload.get(key):
                    resp = requests.put(
                        f"{backend_url}/users/me/{endpoint}/",
                        json=backend_payload[key],
                        headers=headers,
                    )
                    print(f"[INFO] Saved {key}: {resp.status_code}")
        except Exception as e:
            return {"error": f"Failed to save profile to backend: {str(e)}"}

        # Step 4: Return latest backend profile (not just payload)
        try:
            resp = requests.get(f"{backend_url}/users/me", headers=headers)
            return resp.json()
        except:
            return backend_payload

# ------------------------------
# Helpers
# ------------------------------
def welcome_message():
    return "Hello! I'm ElinityAI, your personal social connection guide. Could you start by telling me a little about yourself?"

def transcribe_audio(audio_path):
    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(audio_path) as source:
            recognizer.adjust_for_ambient_noise(source)
            audio_data = recognizer.record(source)
            return recognizer.recognize_google(audio_data)
    except Exception as e:
        return {"error": str(e)}

def text_to_speech(text):
    """Generate TTS from ElevenLabs and return file path"""
    try:
        clean_text = sanitize_for_tts(text)
        audio = eleven_client.text_to_speech.convert(
            voice_id=os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM"),
            model_id=os.getenv("ELEVENLABS_MODEL_ID", "eleven_turbo_v2"),
            text=clean_text,
        )
        tmpfile = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        save(audio, tmpfile.name)
        return tmpfile.name
    except Exception as e:
        print(f"[ERROR] ElevenLabs TTS failed: {e} | Text was: {text}")
        return None

def analyze_and_finalize(state):
    if state is None:
        return {"error": "No conversation recorded. Please start a conversation first."}
    try:
        return state.finalize_user_profile()
    except Exception as e:
        return {"error": f"Error generating user profile: {str(e)}"}

# ------------------------------
# Gradio UI
# ------------------------------
with gr.Blocks(title="ElinityAI Voice Onboarding") as app:
    gr.Markdown("# ElinityAI Voice Onboarding")
    gr.Markdown("Talk with ElinityAI. If your profile exists in backend, we'll fetch it. Otherwise, we'll create one.")

    state = gr.State(None)

    with gr.Row():
        with gr.Column(scale=1):
            audio_input = gr.Audio(sources=["microphone"], type="filepath", label="Your Voice Input")
        with gr.Column(scale=2):
            chat_output = gr.Textbox(label="ElinityAI's Response", interactive=False)
            audio_output = gr.Audio(
                type="filepath",
                label="ElinityAI's Voice Response",
                interactive=False,
                autoplay=True,
                show_download_button=True,
            )

    with gr.Row():
        start_btn = gr.Button("Start Conversation")
        submit_btn = gr.Button("Submit Voice Input")
        analyze_btn = gr.Button("Generate User Profile")

    with gr.Row():
        with gr.Column():
            conversation_display = gr.Textbox(label="Conversation History", interactive=False, lines=10)

    profile_output = gr.JSON(label="Your Generated Profile")

    # Conversation logic
    def start_conversation():
        state_obj = ElinityVoiceOnboarding()
        ai_response = welcome_message()
        speech_file = text_to_speech(ai_response)
        return ai_response, speech_file, state_obj, ai_response

    start_btn.click(
        fn=start_conversation,
        outputs=[chat_output, audio_output, state, conversation_display],
        queue=False,
    )

    def update_conversation(user_audio, state_obj):
        if state_obj is None:
            state_obj = ElinityVoiceOnboarding()
            ai_response = welcome_message()
            speech_file = text_to_speech(ai_response)
            return ai_response, speech_file, state_obj, f"ElinityAI: {ai_response}"

        conversation_text = "\n".join(
            [f"{m['role'].capitalize()}: {m['content']}" for m in state_obj.conversation_history if m["role"] != "system"]
        )

        if user_audio is None:
            ai_response = "I didn't hear anything. Please try again."
            speech_file = text_to_speech(ai_response)
            return ai_response, speech_file, state_obj, conversation_text

        try:
            user_text = transcribe_audio(user_audio)
            if not user_text:
                ai_response = "I didn't hear anything clearly. Could you please speak again?"
                speech_file = text_to_speech(ai_response)
                return ai_response, speech_file, state_obj, conversation_text

            ai_response = state_obj.get_next_prompt(user_text)
            speech_file = text_to_speech(ai_response)
            conversation_text = "\n".join(
                [f"{m['role'].capitalize()}: {m['content']}" for m in state_obj.conversation_history if m["role"] != "system"]
            )
            return ai_response, speech_file, state_obj, conversation_text
        except Exception as e:
            return f"An error occurred: {str(e)}", None, state_obj, conversation_text

    submit_btn.click(
        fn=update_conversation,
        inputs=[audio_input, state],
        outputs=[chat_output, audio_output, state, conversation_display],
        queue=True,
    )

    analyze_btn.click(
        fn=analyze_and_finalize, inputs=[state], outputs=[profile_output], queue=True
    )

# ------------------------------
# Mount into FastAPI instead of launching standalone
# ------------------------------
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()

@router.get("/voice-onboarding")
def voice_onboarding_ui():
    return HTMLResponse(app.launch(
        server_name="0.0.0.0",
        server_port=None,   # disable its own server
        inline=True,
        share=False
    ))
