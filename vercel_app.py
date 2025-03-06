from api import app
from db_setup import Base, Category
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Check database connection and data
database_url = os.getenv('DATABASE_URL')
if database_url:
    try:
        engine = create_engine(database_url)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Check if we have any categories
        category_count = session.query(Category).count()
        logger.info(f"Database contains {category_count} categories")
        
        if category_count == 0:
            logger.warning("No categories found in database. Please run load_data.py to populate the database.")
        
        session.close()
    except Exception as e:
        logger.error(f"Error checking database: {str(e)}")
else:
    logger.warning("DATABASE_URL not set")

# Export the FastAPI app for Vercel
app = app 