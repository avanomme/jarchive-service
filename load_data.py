from db_setup import setup_database
import os
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def main():
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        raise ValueError("DATABASE_URL environment variable is not set")
    
    logger.info("Starting data import...")
    setup_database(database_url)
    logger.info("Data import completed!")

if __name__ == "__main__":
    main() 