from api import app
from db_setup import setup_database
import os
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Set up the database
database_url = os.getenv('DATABASE_URL')
logger.info(f"Database URL: {'Set' if database_url else 'Not set'}")
if database_url:
    try:
        setup_database(database_url)
        logger.info("Database setup completed successfully")
    except Exception as e:
        logger.error(f"Error during database setup: {str(e)}")
else:
    logger.warning("DATABASE_URL not set, skipping database setup")

# Export the FastAPI app for Vercel
app = app 