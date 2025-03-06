import csv
import json
from datetime import datetime, timezone
from collections import defaultdict
import random

def transform_tsv_to_json():
    # Store categories with their clues
    categories = defaultdict(list)
    category_ids = {}
    current_date = datetime.now(timezone.utc).isoformat()
    clue_counter = 1  # For generating unique clue IDs
    category_counter = 1  # For sequential category IDs
    
    # First pass: Generate sequential category IDs based on titles
    with open('combined_season1-40.tsv', 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file, delimiter='\t')
        for row in reader:
            category_title = row['category'].strip()
            if category_title not in category_ids:
                # Use sequential IDs starting from 1
                category_ids[category_title] = category_counter
                category_counter += 1
    
    # Second pass: Create clues with unique IDs but consistent category IDs
    with open('combined_season1-40.tsv', 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file, delimiter='\t')
        for row in reader:
            category_title = row['category'].strip()
            category_id = category_ids[category_title]
            
            # Create clue object with incremental unique ID
            clue = {
                "id": clue_counter,  # Ensure each clue has a unique ID
                "answer": row['answer'].strip(),
                "question": row['comments'].strip(),
                "value": int(row['clue_value']) if row['clue_value'].isdigit() else 200,
                "airdate": f"{row['air_date']}T00:00:00.000Z",
                "created_at": current_date,
                "updated_at": current_date,
                "category_id": category_id,  # Use consistent category ID
                "game_id": clue_counter,  # Simple sequential game ID
                "invalid_count": None
            }
            clue_counter += 1
            
            categories[category_title].append(clue)
    
    # Create final structured data
    structured_data = {
        "categories": [],
        "all_clues": []
    }
    
    # Process each category and its clues
    for title, clues in categories.items():
        # Only include categories that have at least 5 clues
        if len(clues) >= 5:
            category = {
                "id": category_ids[title],
                "title": title,
                "created_at": current_date,
                "updated_at": current_date,
                "clues_count": len(clues)  # Keep the actual clue count
            }
            structured_data["categories"].append(category)
            # Include all clues for this category
            structured_data["all_clues"].extend(clues)
    
    # Save to file
    with open('jservice_data.json', 'w', encoding='utf-8') as f:
        json.dump(structured_data, f, indent=2)

if __name__ == "__main__":
    transform_tsv_to_json() 