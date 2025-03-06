from api import app
from db_setup import setup_database
import os

# Initialize database on startup
setup_database(os.getenv('DATABASE_URL'))

# Export the FastAPI app for Vercel
app = app 