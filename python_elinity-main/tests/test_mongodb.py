#!/usr/bin/env python3
from elinity_ai.embeddings import MongoDB
from dotenv import load_dotenv
import os

# Make sure we load environment variables first
load_dotenv()

# Log the MongoDB URL (masked for security)
mongo_url = os.getenv('MONGO_DB_URL')
if mongo_url:
    # Simple masking for logging
    masked_url = mongo_url
    if '@' in mongo_url:
        parts = mongo_url.split('@')
        credentials = parts[0].split('://')
        if len(credentials) > 1 and ':' in credentials[1]:
            user = credentials[1].split(':')[0]
            masked_url = f"{credentials[0]}://{user}:****@{parts[1]}"
    print(f"MongoDB URL found: {masked_url}")
else:
    print("WARNING: MONGO_DB_URL environment variable not found!")

# Try to connect to MongoDB
try:
    # Test connection with the MongoDB class
    print("\nAttempting to connect with MongoDB class...")
    mongodb = MongoDB(db_name="personas", collection_name="profiles")
    connection_result = mongodb.test()
    
    if connection_result:
        print("✅ Connection successful!")
    else:
        print("❌ Connection failed. Check error messages above.")
    
except Exception as e:
    print(f"❌ Exception during MongoDB connection: {str(e)}")
