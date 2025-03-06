from api import app
from db_setup import setup_database
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up the database
database_url = os.getenv('DATABASE_URL')
if database_url:
    setup_database(database_url)

# Export the FastAPI app for Vercel
app = app 