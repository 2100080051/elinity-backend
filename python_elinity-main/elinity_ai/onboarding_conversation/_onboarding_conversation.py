import google.generativeai as genai 
from typing import List,Optional
import os
from google.genai.types import (
    GenerateContentConfig,
    HarmCategory,
    HarmBlockThreshold,
    HttpOptions,
    SafetySetting,
)
import json
from ._prompts import ONBOARD_PROMPT
from pydantic import BaseModel

class ConversationChat(BaseModel):
    role: str = "system" # "user" or "assistant"
    content: str

class ContinueConversation(BaseModel):
    user_message: str
    asset_url: Optional[str] = None

# Elinity AI Implementation
def welcome_message():
    """Return the welcome message to initialize the conversation."""
    return "Hello! I'm ElinityAI, your personal social connection guide. I'm here to get to know you better so I can help you find meaningful connections. Let's have a relaxed conversation. Could you start by telling me a little about yourself?"

class ElinityOnboardingConversation: 
    
    def __init__(self, model_name="gemini-2.0-flash",system_prompt=ONBOARD_PROMPT,api_key=None,welcome_message="",generation_config=None,safety_settings=None,conversation_history=None):
        """Configure the Gemini API with the API key.
    
        Args:
            custom_api_key: Optional API key to override the one in .env file
            
        Returns:
            bool: True if configuration was successful
        Variables: 
            model_name: The name of the model to use
            system_prompt: The system prompt to use
            api_key: The API key to use
            chat: The chat object
            session_end: Whether the session has ended
            current_question_index: The index of the current question
            conversation_history: List of conversation messages i.e List[ConversationChat]
        Raises:
            ValueError: If no API key is available
        """ 
        self.generation_config = generation_config or  {
            "temperature": 0.7,
            "top_p": 0.95,
            "top_k": 64,
            "max_output_tokens": 150,  # Limit the response length
        }
        
        # Configure generation parameters using the proper syntax
        generation_config = {
            "temperature": 0.7,
            "top_p": 0.95,
            "top_k": 64,
            "max_output_tokens": 150,  # Limit token length for brevity
        }
        
        # Configure safety settings using the proper dictionary format
        safety_settings = {
            "HARM_CATEGORY_DANGEROUS_CONTENT": "BLOCK_MEDIUM_AND_ABOVE",
            "HARM_CATEGORY_HARASSMENT": "BLOCK_MEDIUM_AND_ABOVE",
            "HARM_CATEGORY_HATE_SPEECH": "BLOCK_MEDIUM_AND_ABOVE",
            "HARM_CATEGORY_SEXUALLY_EXPLICIT": "BLOCK_MEDIUM_AND_ABOVE"
        }
        
        self.welcome_message = "Hello! I'm ElinityAI, your personal social connection guide. I'm here to get to know you better so I can help you find meaningful connections. Let's have a relaxed conversation. Could you start by telling me a little about yourself?"
        api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise  ValueError("No API key provided. Either set GOOGLE_API_KEY environment variable in .env file or provide a custom API key.")
        genai.configure(api_key=api_key)
        self.default_role = "system"
        self.model = genai.GenerativeModel(
            model_name=model_name,
            safety_settings=safety_settings,
            generation_config=generation_config
        )
        self.system_prompt = system_prompt
        self.session_end= False 
        self.current_question_index= 0
        self.conversation_history: List[ConversationChat] = conversation_history or []
        
        # Initialize chat with system prompt - using proper format
        self.chat = self.model.start_chat(            
            history=[{"parts":[{"text":system_prompt}],"role":"user"}],
         )
        # Add welcome message to conversation history 
        self.add_message(self.welcome_message)
        
    def parse_histories(self):
        return [chat.model_dump() for chat in self.conversation_history]
        
    def add_message(self,content,role="system"):
        '''Add to conversation history.'''
        chat = ConversationChat(role=role,content=content)
        self.conversation_history.append(chat) 
    
    def get_next_prompt(self,user_message):
        """Get the next prompt from Gemini based on the user's message."""
        if not user_message:
            return "I didn't catch that. Could you please repeat?"
            
        # Add user message to history
        self.add_message(role="user",content=user_message) 
        
        # Format message for Gemini with brevity reminder
        message_with_reminder = f"{user_message}\n\nRemember to keep your response very brief (1-3 sentences) and conversational."
        
        # Send message to Gemini with proper format
        assistant_response = self.chat.send_message(
            {"parts": [{"text": message_with_reminder}]}
        ) 
        
        # Add Gemini Response to conversation history 
        self.add_message(assistant_response.text, role="user")
        
        # Add Gemini Response to conversation history 
        self.add_message(assistant_response.text)
        
        return assistant_response.text 

    def start_conversation(self):
        # Add welcome message to the user 
        self.add_message(self.welcome_message)
        return self.conversation_history 
    
    def get_welcome_message(self):
        return self.parse_histories()[0]
    
    def get_model_list(self): 
        """
        Returns:
           List[GenerativeModel]: The list of available generative AI models
        """
        return [model.name.split('/')[-1] for model in genai.list_models()] 
    
    
model = ElinityOnboardingConversation() 