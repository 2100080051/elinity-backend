from langchain_google_genai import ChatGoogleGenerativeAI
import os 
from dotenv import load_dotenv
from langchain.schema import HumanMessage
from langsmith import Client

load_dotenv()

class ElinityInsights:
    def __init__(self, llm_model: str = "gemini-2.0-flash",langsmith_api_key:str=None):
        self.llm = ChatGoogleGenerativeAI(model=llm_model, temperature=0.7)
        
        # Initialize LangSmith client
        self.langsmith_api_key = langsmith_api_key or os.getenv("LANGSMITH_API_KEY")
        if self.langsmith_api_key:
            os.environ["LANGSMITH_API_KEY"] = self.langsmith_api_key
            self.langsmith_client = Client(api_key=self.langsmith_api_key)
        else:
            raise RuntimeError("Warning: LANGSMITH_API_KEY not found. Using fallback prompt.")

    def generate_insight(self,query,user_id,user_name,score,user_interests):
        try: 
            prompt = self.langsmith_client.pull_prompt('match-insight-generation') 
            formatted_prompt = prompt.format(
                    query=query,
                    user_id=user_id,
                    user_name=user_name, 
                    score=score,
                    user_interests=user_interests
               )
            response = self.llm.invoke([
                    HumanMessage(content=formatted_prompt)
            ])
            return response.content 
        except Exception as e:
            raise RuntimeError(f"Failed to pull insight prompt: {e}")
