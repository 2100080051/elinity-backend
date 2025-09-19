from sentence_transformers import SentenceTransformer
import google.generativeai as genai
import numpy as np
from ._mongodb import MongoDB
import os
from core.logging import logger

# Configure the API key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Set up the model
model = genai.GenerativeModel('gemini-2.0-flash')  # Or 'gemini-1.5-pro' if you have access

class ElinityEmbedding: 
    def __init__(self,model=None): 
        self.model_name = 'all-mpnet-base-v2' 
        self.model = SentenceTransformer(self.model_name)
        self.mongodb =  MongoDB(db_name= "personas",collection_name="profiles")
        
    def generate_dummy_embedding(dimension):
        """Generates a random embedding for testing."""
        return np.random.rand(dimension)

    def _generate_self_description(self,json_data):
        """
        Generates a self-description from the given JSON data using generative AI.
    
        Args:
            json_data: A string containing valid JSON data.
    
        Returns:
            A string containing the generated self-description, or None if an error occurs. 
        """
    
        prompt = f"""
        You are an AI assistant designed to create a concise and engaging self-description from user profile data. Given the following JSON data representing a person's profile, generate a short paragraph describing the person as if they are introducing themselves. 

        **The description must always begin with a greeting and their name (e.g., "Hi, I’m John,...").** 

        Focus on their interests, personality, values, goals, favorite things, and what they are looking for in relationships or life. Be creative and engaging. Use a conversational tone, as if the person were speaking directly to someone.

        JSON Data:
        ```json
        {json_data}
        ```
        """
        try:
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.debug(f"Error during generation: {e}")
            return None
            
    def create_embedding(self,user_profile):
        if isinstance(user_profile,dict): 
            desc = self._generate_self_description(user_profile)
            return desc,self.model.encode(desc)
        if isinstance(user_profile,str): 
            return user_profile,self.model.encode(user_profile)
        return None,None

    def store(self,metadata,profile): 
        try:
            text,embedding = self.create_embedding(profile)
            if not text or not embedding:  
                return text,embedding
            result = self.mongodb.store_embedding(metadata=metadata,text=text,embedding=embedding)
            return result
        except Exception as e:
            logger.debug(f"Error storing embedding: {e}")
            return None

 