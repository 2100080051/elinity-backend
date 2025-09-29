import os
import json
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec

load_dotenv()


class PineconeClient:
    def __init__(self):
        api_key = os.getenv("PINECONE_API_KEY")
        index_name = os.getenv("PINECONE_INDEX_NAME")
        host = os.getenv("PINECONE_HOST")

        if not api_key or not index_name:
            raise RuntimeError("PINECONE_API_KEY and PINECONE_INDEX_NAME must be set in .env")

        # Initialize Pinecone
        self.pc = Pinecone(api_key=api_key)

        # Connect to existing index
        self.index_name = index_name
        self.index = self.pc.Index(self.index_name, host=host)

        
            
    def _extract_text_from_record(self,record):
        """
        Extract meaningful text content from the persona record for embedding
        """
        text_parts = []
        
        # Personal info
        personal = record.get("personal_info", {})
        if personal.get("first_name"):
            text_parts.append(f"First name: {personal['first_name']}")
        if personal.get("last_name"):
            text_parts.append(f"Last name: {personal['last_name']}")
        if personal.get("age") and personal["age"] > 0:
            text_parts.append(f"Age: {personal['age']}")
        if personal.get("gender"):
            text_parts.append(f"Gender: {personal['gender']}")
        if personal.get("location"):
            text_parts.append(f"Location: {personal['location']}")
        if personal.get("occupation"):
            text_parts.append(f"Occupation: {personal['occupation']}")
        if personal.get("education"):
            text_parts.append(f"Education: {personal['education']}")
        if personal.get("relationship_status"):
            text_parts.append(f"Relationship status: {personal['relationship_status']}")
        
        # Interests and hobbies
        interests_hobbies = record.get("interests_and_hobbies", {})
        if interests_hobbies.get("interests"):
            text_parts.append(f"Interests: {', '.join(interests_hobbies['interests'])}")
        if interests_hobbies.get("hobbies"):
            text_parts.append(f"Hobbies: {', '.join(interests_hobbies['hobbies'])}")
        
        # Values and goals
        values_goals = record.get("values_beliefs_and_goals", {})
        if values_goals.get("values"):
            text_parts.append(f"Values: {', '.join(values_goals['values'])}")
        if values_goals.get("personal_goals"):
            text_parts.append(f"Personal goals: {', '.join(values_goals['personal_goals'])}")
        if values_goals.get("professional_goals"):
            text_parts.append(f"Professional goals: {', '.join(values_goals['professional_goals'])}")
        
        # Favorites
        favorites = record.get("favorites", {})
        for category in ["movies", "music", "books", "art"]:
            if favorites.get(category):
                text_parts.append(f"Favorite {category}: {', '.join(favorites[category])}")
        if favorites.get("quotes"):
            text_parts.append(f"Favorite quotes: {', '.join(favorites['quotes'])}")
        
        # Relationship preferences
        rel_prefs = record.get("relationship_preferences", {})
        if rel_prefs.get("looking_for"):
            text_parts.append(f"Looking for in relationships: {', '.join(rel_prefs['looking_for'])}")
        if rel_prefs.get("what_i_offer"):
            text_parts.append(f"What I offer in relationships: {', '.join(rel_prefs['what_i_offer'])}")
        
        # Collaboration preferences
        collab_prefs = record.get("collaboration_preferences", {})
        if collab_prefs.get("areas_of_expertise"):
            text_parts.append(f"Areas of expertise: {', '.join(collab_prefs['areas_of_expertise'])}")
        if collab_prefs.get("achievements"):
            text_parts.append(f"Achievements: {', '.join(collab_prefs['achievements'])}")
        
        # Aspirations
        aspirations = record.get("aspiration_and_reflections", {})
        if aspirations.get("life_goals"):
            text_parts.append(f"Life goals: {', '.join(aspirations['life_goals'])}")
        if aspirations.get("bucket_list"):
            text_parts.append(f"Bucket list: {', '.join(aspirations['bucket_list'])}")
        
        # Personal free form
        free_form = record.get("personal_free_form", {})
        if free_form.get("things_to_share"):
            text_parts.append(f"Personal thoughts: {free_form['things_to_share']}")
        
        # Big Five traits (only include significant scores)
        big_five = record.get("big_five_traits", {})
        significant_traits = []
        for trait, score in big_five.items():
            if score > 0.7:  # High scores
                significant_traits.append(f"High {trait}")
            elif score < 0.3:  # Low scores
                significant_traits.append(f"Low {trait}")
        if significant_traits:
            text_parts.append(f"Personality traits: {', '.join(significant_traits)}")
        
        # Ideal characteristics (only include high scores)
        ideal_chars = record.get("ideal_characteristics", {})
        high_characteristics = [char for char, score in ideal_chars.items() if score > 0.7]
        if high_characteristics:
            text_parts.append(f"Values in others: {', '.join(high_characteristics)}")
        
        return ". ".join(text_parts)

    # Function to prepare record for upsert
    def _prepare_record_for_upsert(self,record):
        """
        Prepare a persona record for upserting to Pinecone
        """
        chunk_text = self._extract_text_from_record(record)
        
        # For Pinecone inference API, we need to structure the record differently
        prepared_record = {
            "id": record["id"],
            "chunk_text": chunk_text
        }
        
        # Add metadata fields directly to the record (not nested under 'metadata')
        if record.get("email"):
            prepared_record["email"] = str(record["email"])
        
        if record.get("created_at"):
            prepared_record["created_at"] = str(record["created_at"])
        
        if record.get("last_login"):
            prepared_record["last_login"] = str(record["last_login"])
        
        # Boolean flags
        prepared_record["has_personal_info"] = bool(any([
            record.get("personal_info", {}).get("first_name"),
            record.get("personal_info", {}).get("location"),
            record.get("personal_info", {}).get("occupation")
        ]))
        
        prepared_record["has_interests"] = bool(record.get("interests_and_hobbies", {}).get("interests"))
        prepared_record["has_goals"] = bool(record.get("values_beliefs_and_goals", {}).get("personal_goals"))
        
        # Add some additional useful metadata
        personal = record.get("personal_info", {})
        if personal.get("age") and personal["age"] > 0:
            prepared_record["age"] = int(personal["age"])
        
        if personal.get("location"):
            prepared_record["location"] = str(personal["location"])
        
        if personal.get("occupation"):
            prepared_record["occupation"] = str(personal["occupation"])
        
        return prepared_record
        
    # For bulk upsert of multiple records:
    def bulk_upsert_personas(self,records, namespace="personas", batch_size=100):
        """
        Bulk upsert persona records to Pinecone
        """
        prepared_records = [self._prepare_record_for_upsert(record) for record in records]
    
        # Process in batches
        for i in range(0, len(prepared_records), batch_size):
            batch = prepared_records[i:i + batch_size]
            self.index.upsert_records(
                namespace=namespace,
                records=batch
            )
            print(f"Upserted batch {i//batch_size + 1}: {len(batch)} records")
           
pinecone_client = PineconeClient()
  