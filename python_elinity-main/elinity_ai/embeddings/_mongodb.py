from pymongo import MongoClient
import os
from core.logging import logger
from dotenv import load_dotenv

load_dotenv()

class MongoDB: 
    def __init__(self,collection_name,db_name,dimension=128): 
        # Ensure environment variables are loaded
        load_dotenv()
        
        self.db_name = db_name
        self.collection_name = collection_name
        self.dimension = dimension
        
        # Get connection string and log useful debug info
        _connection_string = os.getenv('MONGO_DB_URL')
        if not _connection_string: 
            logger.error("MONGO_DB_URL environment variable is not set")
            raise RuntimeError("MONGO_DB_URL is required.") 
            
        # Mask password for logging
        masked_url = self._mask_connection_string(_connection_string)
        logger.debug(f"Attempting to connect to MongoDB with URL: {masked_url}")
        
        try:
            self.client = MongoClient(_connection_string, serverSelectionTimeoutMS=5000)
            self.db = self.client[self.db_name] 
            self.collection = self.db[self.collection_name]
            logger.debug(f"MongoDB client initialized for database '{self.db_name}' and collection '{self.collection_name}'")
        except Exception as e:
            logger.error(f"Error initializing MongoDB client: {str(e)}")
            raise
        

    def _mask_connection_string(self, connection_string):
        """Mask the password in the connection string for secure logging"""
        if not connection_string or '://' not in connection_string:
            return connection_string
        
        parts = connection_string.split('://')
        if '@' in parts[1]:
            auth_part = parts[1].split('@')[0]
            if ':' in auth_part:
                user = auth_part.split(':')[0]
                return f"{parts[0]}://{user}:****@{parts[1].split('@')[1]}"
        return connection_string.replace('//', '//****:****@')
    
    def test(self): 
        """Test the MongoDB connection with detailed error reporting"""
        try:
            # Set a short timeout for the server selection
            result = self.client.admin.command('ping')
            logger.debug(f"Successfully connected to MongoDB Atlas! Server info: {result}")
            return True
        except Exception as e:
            logger.error(f"MongoDB connection error: {str(e)}")
            
            # Provide more context about what might be wrong
            if "ServerSelectionTimeoutError" in str(e):
                logger.error("The application couldn't connect to MongoDB server. This could be due to:")
                logger.error("1. Network connectivity issues")
                logger.error("2. Incorrect connection string")
                logger.error("3. IP address not whitelisted in MongoDB Atlas")
            elif "Authentication failed" in str(e):
                logger.error("MongoDB authentication failed. Check username and password.")
                
            return False
            
    def store_embedding(self,metadata,text, embedding):
        """Stores text and its embedding in MongoDB."""
        print('store_embedding')
        try:
            document = {
                "text": text,
                "metadata": metadata,
                "embedding_tsf": embedding.tolist()  # Convert numpy array to list
            }
            print(f"Document: {document}")
            result = self.collection.insert_one(document)
            logger.debug(f"Inserted document with ID: {result.inserted_id}")
            return result
        except Exception as e:
            logger.debug(f"Error storing embedding: {e}")
            return None

    def create_vector_search_index(self):
        """Creates a vector search index on the collection if one doesn't exist.
           This function assumes you are using MongoDB Atlas.  You can also create
           the index through the Atlas UI.
        """
        index_name = "vectorSearchIndex"
        try:
            # Check if the index already exists
            existing_indexes = self.collection.index_information()
            if index_name in existing_indexes:
                print(f"Vector search index '{index_name}' already exists.")
                return
    
            # Create the vector search index using Atlas Search syntax
            index_definition = {
                "analyzer": "default",
                "mappings": {
                    "dynamic": False,
                    "fields": {
                        "embedding": {
                            "dimensions": self.dimension,
                            "similarity": "cosine",
                            "type": "vector"
                        }
                    }
                },
                "name": index_name,
                "type": "vectorSearch"
            }
    
            self.db.command("createSearchIndex", self.collection_name, definition=index_definition)
            print(f"Vector search index '{index_name}' created successfully.")
    
        except Exception as e:
            print(f"Error creating vector search index: {e}")

    def search_by_embedding(self,query_embedding, top_k=5):
        """Searches for documents with embeddings similar to the query using Atlas Vector Search."""
        index_name = "vectorSearchIndex"
        try:
            pipeline = [
                {
                    "$vectorSearch": {
                        "index": index_name,  # Name of your vector search index
                        "path": "embedding",  # Field containing the embedding
                        "queryVector": query_embedding.tolist(),
                        "numCandidates": 100,  # Number of candidates to consider (adjust as needed)
                        "limit": top_k
                    }
                },
                {
                    "$project": {
                        "_id": 1,
                        "text": 1,
                        "similarityScore": {"$meta": "vectorSearchScore"}
                    }
                }
            ]
    
            results = list(self.collection.aggregate(pipeline))
            return results

        except Exception as e:
            print(f"Error performing vector search: {e}")
            return []
 