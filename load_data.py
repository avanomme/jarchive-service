import os
import json
import logging
import time
from pathlib import Path
from supabase import create_client, Client
from dotenv import load_dotenv
from typing import List, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize Supabase client with increased timeout
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

def load_json_from_storage(file_path: str, max_retries: int = 3) -> dict:
    """Load JSON file from Supabase storage with retry logic."""
    for attempt in range(max_retries):
        try:
            # Download file from storage
            response = supabase.storage.from_("jservice-data").download(file_path)
            return json.loads(response)
        except Exception as e:
            if attempt == max_retries - 1:
                logger.error(f"Error loading {file_path} from storage after {max_retries} attempts: {str(e)}")
                raise
            wait_time = (2 ** attempt) * 5  # Exponential backoff: 5s, 10s, 20s
            logger.warning(f"Attempt {attempt + 1} failed, retrying in {wait_time} seconds...")
            time.sleep(wait_time)

def bulk_upsert_categories_and_clues(data: dict, batch_size: int = 1000):
    """Bulk insert or update categories and clues in the database."""
    try:
        # Prepare all categories and clues data
        categories_data = []
        clues_data = []
        
        for category in data["categories"]:
            categories_data.append({
                "id": category["id"],
                "title": category["title"],
                "created_at": category["created_at"],
                "updated_at": category["updated_at"],
                "clues_count": category["clues_count"]
            })
            
            if category["clues"]:
                for clue in category["clues"]:
                    clues_data.append({
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
                    })
        
        # Bulk upsert categories
        logger.info(f"Bulk upserting {len(categories_data)} categories...")
        for i in range(0, len(categories_data), batch_size):
            batch = categories_data[i:i + batch_size]
            try:
                # Use upsert operation (insert if not exists, update if exists)
                supabase.table("categories").upsert(batch).execute()
            except Exception as e:
                logger.error(f"Error bulk upserting categories batch: {str(e)}")
                continue
        
        # Bulk upsert clues
        logger.info(f"Bulk upserting {len(clues_data)} clues...")
        for i in range(0, len(clues_data), batch_size):
            batch = clues_data[i:i + batch_size]
            try:
                # Use upsert operation (insert if not exists, update if exists)
                supabase.table("clues").upsert(batch).execute()
            except Exception as e:
                logger.error(f"Error bulk upserting clues batch: {str(e)}")
                continue
            
            # Add a small delay between large batches to prevent rate limiting
            if i + batch_size < len(clues_data):
                time.sleep(0.5)
                
    except Exception as e:
        logger.error(f"Error in bulk_upsert_categories_and_clues: {str(e)}")
        raise

def main():
    """Main function to load all season data."""
    try:
        # List all JSON files in the storage bucket
        files = supabase.storage.from_("jservice-data").list()
        
        for file in files:
            if file["name"].endswith(".json"):
                try:
                    logger.info(f"Processing {file['name']}...")
                    data = load_json_from_storage(file["name"])
                    bulk_upsert_categories_and_clues(data)
                    logger.info(f"Successfully processed {file['name']}")
                except Exception as e:
                    logger.error(f"Error processing file {file['name']}: {str(e)}")
                    continue
                
                # Add a small delay between files
                time.sleep(1)
                
    except Exception as e:
        logger.error(f"Error in main process: {str(e)}")
        raise

if __name__ == "__main__":
    main() 