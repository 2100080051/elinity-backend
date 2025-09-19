import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

class ElinitySmartJournal: 
    def __init__(self): 
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        self.model =  genai.GenerativeModel('gemini-2.0-flash')  # Or 'gemini-1.5-pro' if you have access

    def generate_insights(self,transcript):
        """
        Generates a self-description from the given JSON data using generative AI.
    
        Args:
            json_data: A string containing valid JSON data.
    
        Returns:
            A string containing the generated self-description, or None if an error occurs.
        """
    
        prompt = f""" 
            Analyze the following transcript and generate comprehensive AI insights that:
    
            1. Identify the main topics, themes, and key concepts present in the text
            
            2. For each identified topic:
               - Extract the core information and key details
               - Organize related facts and explanations
               - Highlight any examples, case studies, or real-world applications mentioned
               - Note any specialized terminology with clear definitions
            
            3. Develop analytical insights including:
               - Patterns, relationships, or connections between different concepts
               - Underlying principles or frameworks that emerge from the content
               - Potential applications or implications of this information
               - Notable gaps or areas where further exploration would be valuable
            
            4. Structure the information for clarity and reference:
               - Create a hierarchical organization of main ideas and supporting details
               - Develop a concise summary of the most important takeaways
               - Highlight any statistical data, research findings, or expert opinions
               - Identify any chronological sequences or processes described
            
            5. Transform the analysis into practical knowledge by:
               - Extracting actionable insights relevant to different stakeholders
               - Formulating questions that promote deeper understanding
               - Suggesting how this information could be applied in various contexts
               - Connecting the content to broader fields or disciplines where relevant
            
            Format the output as a well-structured, professionally-written analysis suitable for inclusion in a specialized journal or knowledge base.
            
            TRANSCRIPT:
            {transcript} 
            """ 
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Error during generation: {e}")
            return None



# if __name__ == "__main__":
#     sm_journal = SmartJournal()
#     result = sm_journal.generate_insights(text) 
#     print(result)