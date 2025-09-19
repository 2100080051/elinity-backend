# session.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from utils.settings import DATABASE_URL, REDIS_HOST, REDIS_PORT, REDIS_DB, REDIS_PASSWORD
import redis

# Load environment variables
load_dotenv()


# SQLAlchemy setup
engine = create_engine(DATABASE_URL)
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# PostgreSQL Database dependency
def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()

# Raw PostgreSQL client connection if needed
def get_client():
    return engine.connect()

# Redis client dependency
def get_redis_client():
    redis_client = redis.Redis(
        host=REDIS_HOST, 
        port=REDIS_PORT,
        db=REDIS_DB,
        password=REDIS_PASSWORD,
        decode_responses=False  # Keep as bytes to avoid encoding issues
    )
    try:
        yield redis_client
    finally:
        redis_client.close()
        


    