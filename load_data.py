import os
import json
import logging
from pathlib import Path
from supabase import create_client, Client
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize Supabase client
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

def load_json_from_storage(file_path: str) -> dict:
    """Load JSON file from Supabase storage."""
    try:
        # Download file from storage
        response = supabase.storage.from_("jservice-data").download(file_path)
        return json.loads(response)
    except Exception as e:
        logger.error(f"Error loading {file_path} from storage: {str(e)}")
        raise

def upsert_categories_and_clues(data: dict):
    """Insert or update categories and clues in the database."""
    try:
        # Process categories
        for category in data["categories"]:
            # Check if category exists
            existing_category = supabase.table("categories").select("*").eq("id", category["id"]).execute()
            
            category_data = {
                "id": category["id"],
                "title": category["title"],
                "created_at": category["created_at"],
                "updated_at": category["updated_at"],
                "clues_count": category["clues_count"]
            }
            
            if existing_category.data:
                # Update existing category
                supabase.table("categories").update(category_data).eq("id", category["id"]).execute()
            else:
                # Insert new category
                supabase.table("categories").insert(category_data).execute()
            
            # Process clues for this category
            if category["clues"]:
                for clue in category["clues"]:
                    clue_data = {
                        "id": clue["id"],
                        "answer": clue["answer"],
                        "question": clue["question"],
                        "value": clue["value"],
                        "airdate": clue["airdate"],
                        "created_at": clue["created_at"],
                        "updated_at": clue["updated_at"],
                        "category_id": category["id"],
                        "game_id": clue["game_id"],
                        "invalid_count": clue["invalid_count"]
                    }
                    
                    # Check if clue exists
                    existing_clue = supabase.table("clues").select("*").eq("id", clue["id"]).execute()
                    
                    if existing_clue.data:
                        # Update existing clue
                        supabase.table("clues").update(clue_data).eq("id", clue["id"]).execute()
                    else:
                        # Insert new clue
                        supabase.table("clues").insert(clue_data).execute()
                
    except Exception as e:
        logger.error(f"Error inserting/updating data: {str(e)}")
        raise

def main():
    """Main function to load all season data."""
    try:
        # List all JSON files in the storage bucket
        files = supabase.storage.from_("jservice-data").list()
        
        for file in files:
            if file["name"].endswith(".json"):
                logger.info(f"Processing {file['name']}...")
                data = load_json_from_storage(file["name"])
                upsert_categories_and_clues(data)
                logger.info(f"Successfully processed {file['name']}")
                
    except Exception as e:
        logger.error(f"Error in main process: {str(e)}")
        raise

if __name__ == "__main__":
    main() 