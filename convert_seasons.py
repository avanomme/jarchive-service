import os
import json
import csv
from datetime import datetime, timezone
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def convert_tsv_to_json(tsv_file):
    """Convert a single TSV file to our required JSON format."""
    categories = {}
    category_counter = 1
    clue_counter = 1
    current_date = datetime.now(timezone.utc)
    
    # First pass: Create categories
    with open(tsv_file, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file, delimiter='\t')
        for row in reader:
            category_title = row['category'].strip()
            if category_title not in categories:
                category = {
                    "id": category_counter,
                    "title": category_title,
                    "created_at": current_date.isoformat(),
                    "updated_at": current_date.isoformat(),
                    "clues_count": 0,
                    "clues": []
                }
                categories[category_title] = category
                category_counter += 1
    
    # Second pass: Create clues and update category counts
    category_clue_counts = {}
    with open(tsv_file, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file, delimiter='\t')
        for row in reader:
            category_title = row['category'].strip()
            category = categories[category_title]
            
            # Create clue
            clue = {
                "id": clue_counter,
                "answer": row['answer'].strip(),
                "question": row['comments'].strip(),
                "value": int(row['clue_value']) if row['clue_value'].isdigit() else 200,
                "airdate": datetime.strptime(row['air_date'] + "T00:00:00.000Z", "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc).isoformat(),
                "created_at": current_date.isoformat(),
                "updated_at": current_date.isoformat(),
                "category_id": category["id"],
                "game_id": clue_counter,
                "invalid_count": None
            }
            category["clues"].append(clue)
            
            # Update category clue count
            if category["id"] not in category_clue_counts:
                category_clue_counts[category["id"]] = 0
            category_clue_counts[category["id"]] += 1
            
            clue_counter += 1
    
    # Update category clue counts and filter out categories with less than 5 clues
    filtered_categories = {}
    for category_title, category in categories.items():
        count = category_clue_counts.get(category["id"], 0)
        if count >= 5:
            category["clues_count"] = count
            filtered_categories[category["id"]] = category
    
    return filtered_categories

def main():
    # Create output directory if it doesn't exist
    output_dir = Path("json_seasons")
    output_dir.mkdir(exist_ok=True)
    
    # Process each season file
    seasons_dir = Path("seasons")
    for tsv_file in seasons_dir.glob("season*.tsv"):
        logger.info(f"Processing {tsv_file.name}...")
        try:
            # Convert TSV to JSON
            categories = convert_tsv_to_json(tsv_file)
            
            # Save to JSON file
            output_file = output_dir / f"{tsv_file.stem}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump({"categories": list(categories.values())}, f, indent=2)
            
            logger.info(f"Successfully converted {tsv_file.name} to {output_file.name}")
            
        except Exception as e:
            logger.error(f"Error processing {tsv_file.name}: {str(e)}")
            continue

if __name__ == "__main__":
    main() 