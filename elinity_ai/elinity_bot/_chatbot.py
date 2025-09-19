from pydantic import Field 
from langchain_core.language_models.llms import LLM
from google import generativeai as genai
from typing import Optional, List
from google.generativeai import GenerativeModel
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables import RunnableSequence,Runnable
import os
from dotenv import load_dotenv

load_dotenv()

class GeminiLLM(LLM):
    model_name: str = Field(default="gemini-1.5-flash")
    model: GenerativeModel = Field(default=None, exclude=True)

    @property
    def _llm_type(self) -> str:
        return "gemini_custom"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        self.model = genai.GenerativeModel(self.model_name)

    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        response = self.model.generate_content(prompt)
        return response.text if hasattr(response, 'text') else response.parts[0].text


class ExtractTextRunnable(Runnable):
    def invoke(self, input, *args, **kwargs):
        return input['text']


class ElinityChatbot: 
    def __init__(self,model_name='gemini-2.0-flash',history=[]): 
        self.model =  GeminiLLM(model_name='gemini-2.0-flash')  
        self.template = """
            You are Elinity, an AI assistant embedded in group chats. Your role is to help, but only when it's genuinely useful. Keep the following principles and behaviors in mind at all times:
        
            - Contextual Sensitivity: Read the room before speaking.
            - Conversational Awareness: Don’t interrupt unless there’s clear value.
            - Signal-Driven Proactivity: Speak only when helpful or asked.
            - Adapt to the group's tone, humor, and energy.
            - Stay silent if things are flowing naturally.
            - Triggers to speak: planning, indecision, low energy, direct mention, confusion, conflict.
            - Stay brief, human-like, and emotionally calibrated.
            
            Here is the current conversation:
            {conversation}
            
            What should Elinity say next?
            Respond ONLY with a JSON object like this: {{ "message": "<next message>" }}
            """ 
        self.history = history
        self.prompt = PromptTemplate(
                        input_variables=["conversation"],
                        template=self.template
                  )
        self.parser = JsonOutputParser() 
        self.chain = RunnableSequence(self.prompt,self.model,self.parser)

    def _get_conversation_text(self):
        conversation_text = "\n".join(f"{msg.sender}: {msg.message}" for msg in self.history)
        return conversation_text
    
    def get_message(self):
        result = self.chain.invoke({"conversation": self._get_conversation_text()})
        return result['message']

