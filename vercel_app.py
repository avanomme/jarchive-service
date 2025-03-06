from api import app
from db_setup import setup_database
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize database on startup
try:
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        setup_database(database_url)
        print("Database setup completed successfully!")
    else:
        print("Warning: DATABASE_URL not set, skipping database setup")
except Exception as e:
    print(f"Error during database setup: {str(e)}")

# Export the FastAPI app for Vercel
app = app 