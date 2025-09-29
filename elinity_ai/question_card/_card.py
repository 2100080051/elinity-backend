from langchain_core.language_models.llms import LLM
from google.generativeai import GenerativeModel
from dotenv import load_dotenv
import os
from typing import Dict, List, Optional,Literal,Any
from pydantic import BaseModel, Field
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.runnables import RunnableSequence
from langsmith import Client
from enum import Enum 
from dataclasses import dataclass
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from core.logging import logger

load_dotenv()

# --- Placeholder GeminiLLM for demonstration ---
# Replace this with your actual GeminiLLM import and implementation
class GeminiLLM(LLM):
    model_name: str = Field(default="gemini-2.0-flash")
    model: GenerativeModel = Field(default=None, exclude=True)

    @property
    def _llm_type(self) -> str:
        return "gemini_custom"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        from google import generativeai as genai
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        self.model = genai.GenerativeModel(self.model_name)

    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        response = self.model.generate_content(prompt)
        return response.text if hasattr(response, 'text') else response.parts[0].text



@dataclass
class PerformanceResult:
    """Container for performance metrics"""
    execution_time: float
    cards_generated: int
    cards_per_second: float
    method: str
    success_rate: float = 1.0

# Pydantic Models
class TagType(str, Enum):
    RELATIONSHIP = "relationship"
    FRIENDS = "friends"
    FAMILY = "family"
    SELF = "self"
    GENERAL = "general"
    GAMES_ACTIVITIES = "games_activities"

class CardType(str, Enum):
    QUESTION = "question"
    PROMPT = "prompt"
    SUGGESTION = "suggestion"

class QuestionCard(BaseModel):
    """Structured question/prompt card model"""
    text: str = Field(description="The main question, prompt, or suggestion text")
    card_type: CardType = Field(description="Type of card: question, prompt, or suggestion")
    tags: List[TagType] = Field(description="Relevant tags for categorization")
    difficulty_level: Literal["easy", "medium", "hard"] = Field(description="Complexity level of the question")
    estimated_time_minutes: int = Field(description="Estimated time to think about or discuss this card")
    
    # System fields (set by backend)
    meta_note: Optional[str] = Field(default="", description="User-added notes")
    favourite: bool = Field(default=False, description="Whether user has starred this card")
    shown_previously: bool = Field(default=False, description="Whether this card has been shown before")
    image_file: Optional[str] = Field(default=None, description="Path to associated image file")
    liked: bool = Field(default=False, description="Whether user liked this card")
    private: bool = Field(default=True, description="Whether this is a private or public card")
    sound_file: Optional[str] = Field(default=None, description="Path to associated sound file (future feature)")


class QuestionCardGenerator:
    
    def __init__(self, 
                 api_key: Optional[str] = None, 
                 model_name: str = "gemini-2.0-flash",
                 langsmith_api_key: Optional[str] = None,
                 prompt_repo: str = "question-card-generator"):
        """
        Initialize the search mode system with LangChain and structured output
        
        Args:
            api_key: Google API key (optional, will use env var if not provided)
            model_name: Gemini model name to use
            langsmith_api_key: LangSmith API key (optional, will use env var if not provided)
            prompt_repo: LangSmith prompt repository name
        """
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise RuntimeError("GOOGLE_API_KEY is required. Please set in environment variables.")
        
        # Store prompt_repo as instance variable
        self.prompt_repo = prompt_repo
        
        # Initialize LangSmith client
        self.langsmith_api_key = langsmith_api_key or os.getenv("LANGSMITH_API_KEY")
        if self.langsmith_api_key:
            os.environ["LANGSMITH_API_KEY"] = self.langsmith_api_key
            self.langsmith_client = Client(api_key=self.langsmith_api_key)
        else:
            print("Warning: LANGSMITH_API_KEY not found. Will use fallback prompt.")
            self.langsmith_client = None
            
        # Initialize LangChain components - Fixed the class name
        self.llm = GeminiLLM(model_name=model_name)  
        
        # Set up Pydantic output parser
        self.output_parser = PydanticOutputParser(pydantic_object=QuestionCard)
        
        # Create fallback prompt template
        self.prompt_template = self._load_prompt_from_langsmith(prompt_repo)
        
        # Create the chain
        self.chain = RunnableSequence(self.prompt_template, self.llm, self.output_parser)
    

    def _load_prompt_from_langsmith(self, prompt_repo: str) -> PromptTemplate:
        """
        Load prompt from LangSmith hub or use fallback
        
        Args:
            prompt_repo: LangSmith prompt repository name
            
        Returns:
            PromptTemplate: Loaded or fallback prompt template
        """
        try:
            if self.langsmith_client:
                # Try to pull from LangSmith hub 
                prompt_template = self.langsmith_client.pull_prompt(prompt_repo)
                print(f"Successfully loaded prompt from LangSmith: {prompt_repo}")
                return prompt_template
            else:
                raise Exception("LangSmith client not initialized")
                
        except Exception as e:
            raise RuntimeError(f"Failed to load prompt from LangSmith ({e}). Using fallback prompt.")
    
    def generate_single_card(self, user_profile: any) -> QuestionCard:
        """Generate a single question card based on user profile""" 
        response = self.chain.invoke({
            'user_profile_json': user_profile, 
            'format_instructions': self.output_parser.get_format_instructions()
        })
        return response
        
    def generate_batch_cards(self, profile: Dict[str, Any], count: int=25) -> List[Dict[str, Any]]:
        """Generate multiple cards sequentially (original method)"""
        cards = []
        for i in range(count):
            try:
                card = self.generate_single_card(profile)
                cards.append(card)
            except Exception as e:
                print(f"Error generating card {i + 1}: {e}")
                continue
        return cards
    
    def generate_batch_cards_with_timing(self, profile: Dict[str, Any], count: int=25) -> PerformanceResult:
        """Generate cards with performance tracking"""
        start_time = time.time()
        
        cards = self.generate_batch_cards(profile, count)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        return PerformanceResult(
            execution_time=execution_time,
            cards_generated=len(cards),
            cards_per_second=len(cards) / execution_time if execution_time > 0 else 0,
            method="sequential",
            success_rate=len(cards) / count if count > 0 else 0
        )


class OptimizedCardGenerator:
    """
    Optimized Card Generator using threading.
    Defaults to 16 workers based on observed performance.
    """

    def __init__(self, max_workers: int = 25):
        """
        Initializes the generator.

        Args:
            max_workers (int): The number of threads to use. Defaults to 25,
                               which was found to be optimal in tests.
        """
        self.max_workers = max_workers 
        # Consider initializing ONE QuestionCardGenerator or its prompt/LLM
        # here if it's thread-safe or can be made so, to avoid
        # repeated initializations (like prompt loading) in each thread.
        self.generator = QuestionCardGenerator()

    def _generate_card_thread(self, profile: Dict[str, Any], card_id: int) -> Dict[str, Any]:
        """
        Thread worker method to generate a single card.
        """
        # If QuestionCardGenerator isn't thread-safe or needs per-thread
        # instances, create it here. Otherwise, use a shared instance.
        try:
            return self.generator.generate_single_card(profile)
        except Exception as e:
            print(f"Thread worker error for card {card_id}: {e}")
            return None

    def generate_cards(self, profile: Dict[str, Any], count: int) -> List[Dict[str, Any]]:
        """
        Generate a batch of cards using optimized threading.

        Args:
            profile (Dict[str, Any]): The user profile for card generation.
            count (int): The number of cards to generate.

        Returns:
            List[Dict[str, Any]]: A list of generated cards.
        """
        cards = []
        logger.info(f"🚀 Generating {count} cards using {self.max_workers} workers...")
        start_time = time.time()

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_id = {
                executor.submit(self._generate_card_thread, profile, i + 1): i + 1
                for i in range(count)
            }

            # Collect results as they complete
            for future in as_completed(future_to_id):
                card_id = future_to_id[future]
                try:
                    card = future.result()
                    if card is not None:
                        cards.append(card)
                    else:
                        print(f"⚠️ Card {card_id} generation resulted in None.")
                except Exception as e:
                    print(f"❌ Error processing card {card_id}: {e}")

        end_time = time.time()
        execution_time = end_time - start_time
        cards_per_second = len(cards) / execution_time if execution_time > 0 else 0

        logger.info(f"✅ Generated {len(cards)}/{count} cards in {execution_time:.2f}s "
              f"({cards_per_second:.1f} cards/sec).")

        return cards


# --- Example Usage for an API ---
# if __name__ == "__main__":


#     # 1. Create an instance of the generator (uses 16 threads by default)
#     card_generator = OptimizedCardGenerator()

#     # 2. Define how many cards you need
#     num_cards_needed = 25

#     # 3. Generate the cards
#     # generated_cards_list = card_generator.generate_cards(profile, num_cards_needed)

#     # 4. Use the generated cards (e.g., return them in an API response)
#     print(f"\n--- API Response Preview (First 5 Cards) ---")
#     # for card in generated_cards_list[:5]:
#     #     print(card)
#     print("--- End Preview ---")

#     max_workers= 25
#     # You can also override the worker count if needed
#     print(f"\n--- Testing with fewer workers (e.g., {max_workers}) ---")
#     low_worker_generator = OptimizedCardGenerator(max_workers=max_workers)
#     low_worker_cards = low_worker_generator.generate_cards(profile, 25)
#     print(f"Generated {len(low_worker_cards)} cards with {max_workers} workers.")