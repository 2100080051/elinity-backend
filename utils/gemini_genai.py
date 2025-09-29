import os
import re
import json
import requests
from dotenv import load_dotenv
import google.generativeai as genai
from pydantic import ValidationError

# Use Elinity-AI schema (camelCase aliases)
from schemas.user import User


load_dotenv()


def configure_genai(custom_api_key=None):
    """Configure Gemini with API key."""
    api_key = custom_api_key or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("No API key provided. Set GOOGLE_API_KEY in .env or pass a custom key.")
    genai.configure(api_key=api_key)
    return genai


def get_model_list():
    try:
        models = genai.list_models()
        return [m.name.split("/")[-1] for m in models]
    except Exception as e:
        print("Error fetching models:", e)
        return []


def transform_for_backend(profile: dict) -> dict:
    """Convert Elinity-AI (camelCase) to backend (snake_case)."""
    return {
        "personal_info": profile.get("personalInfo"),
        "big_five_traits": profile.get("bigFiveTraits"),
        "mbti_traits": profile.get("mbtiTraits"),
        "psychology": profile.get("psychology"),
        "interests_and_hobbies": profile.get("interestsAndHobbies"),
        "values_beliefs_and_goals": profile.get("valuesBeliefsAndGoals"),
        "favorites": profile.get("favorites"),
        "relationship_preferences": profile.get("relationshipPreferences"),
        "friendship_preferences": profile.get("friendshipPreferences"),
        "collaboration_preferences": profile.get("collaborationPreferences"),
        "personal_free_form": profile.get("personalFreeForm"),
        "intentions": profile.get("intentions"),
        "aspiration_and_reflections": profile.get("aspirationAndReflections"),
        "ideal_characteristics": profile.get("idealCharacteristics"),
    }


class GeminiGenAIClient:
    def __init__(self, api_key=None, model_name="gemini-2.0-flash"):
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("No API key provided. Set GOOGLE_API_KEY in .env or pass a custom key.")
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(model_name)

    def _clean_json_text(self, raw: str) -> str:
        """Strip ```json fences / markdown and extract first { ... } block."""
        s = (raw or "").strip()
        if s.startswith("```json"):
            s = s[len("```json") :].strip()
        if s.startswith("```"):
            s = s.strip("`").strip()
        if s.endswith("```"):
            s = s[:-3].strip()
        if not (s.startswith("{") and s.endswith("}")):
            m = re.search(r"\{.*\}", s, re.DOTALL)
            if m:
                s = m.group(0).strip()
        return s

    def generate_user_profile(self, conversation_history):
        """
        Generate a structured user profile using Gemini and validate against schema.
        Returns: dict matching schemas.users.User (camelCase keys).
        """
        try:
            conversation_text = "\n".join(
                f"{m['role']}: {m['content']}" for m in conversation_history
            )
            prompt = (
                "Extract a user profile as VALID JSON ONLY (no markdown, no code fences), "
                "strictly following this JSON schema:\n\n"
                f"{User.model_json_schema()}\n\n"
                "Conversation:\n"
                f"{conversation_text}\n\n"
                "Respond with JSON only."
            )
            response = self.model.generate_content(prompt)
            raw = (response.text or "").strip()
            print("Raw Gemini response:", raw)

            json_str = self._clean_json_text(raw)
            data = json.loads(json_str)

            user = User(**data)  # validate
            return user.dict()

        except (json.JSONDecodeError, ValidationError) as e:
            print("Profile generation failed:", e)
            return {"error": str(e), "raw_response": (raw if "raw" in locals() else "")}
        except Exception as e:
            print("Gemini API error:", e)
            return {"error": str(e)}

    def get_access_token(self):
        """Fetch a fresh access token from backend using username/password."""
        backend_url = os.getenv("BACKEND_URL", "http://localhost:8081")
        username = os.getenv("USERNAME")
        password = os.getenv("PASSWORD")
        if not username or not password:
            raise ValueError("USERNAME and PASSWORD must be set in .env for auto login")
        try:
            resp = requests.post(
                f"{backend_url}/auth/token",
                data={"username": username, "password": password}
            )
            resp.raise_for_status()
            return resp.json().get("access_token")
        except Exception as e:
            print(f"[ERROR] Failed to fetch access token: {e}")
            return None

