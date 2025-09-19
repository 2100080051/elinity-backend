import logging
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get environment and set default log level based on it
ENV = os.getenv("ENV", "development").lower()

# Configure the root logger
root_logger = logging.getLogger()

# Default log level based on environment
if ENV == "production":
    DEFAULT_LOG_LEVEL = logging.INFO
else:
    DEFAULT_LOG_LEVEL = logging.DEBUG

# Allow override through environment variable
LOG_LEVEL = os.getenv("LOG_LEVEL", "").upper()
if LOG_LEVEL in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
    level = getattr(logging, LOG_LEVEL)
else:
    level = DEFAULT_LOG_LEVEL

# Configure the root logger
root_logger.setLevel(level)

# Add a stream handler if not already added
if not root_logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    root_logger.addHandler(handler)

# Create and configure a module logger
logger = logging.getLogger(__name__)

# Send an initialization message at the appropriate level
if ENV != "production":
    logger.debug("Logging initialized with level: %s", logging.getLevelName(level))
else:
    logger.info("Logging initialized with level: %s", logging.getLevelName(level))