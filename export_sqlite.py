import sqlite3
import json
import logging
from pathlib import Path
from typing import Dict, List, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_categories_with_clues(db_path: str) -> List[Dict[str, Any]]:
    """Get all categories with their associated clues from the SQLite database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all categories with their clues
    cursor.execute("""
        SELECT 
            c.id,
            c.name as title,
            c.notes,
            c.index,
            cl.id as clue_id,
            cl.value,
            cl.index as clue_index,
            cl.question,
            cl.answer,
            cl.notes as clue_notes,
            cl.double
        FROM categories c
        LEFT JOIN clues cl ON c.id = cl.category_id
        ORDER BY c.id, cl.index
    """)
    
    # Organize the data into categories with their clues
    categories: Dict[int, Dict[str, Any]] = {}
    
    for row in cursor.fetchall():
        cat_id = row[0]
        if cat_id not in categories:
            categories[cat_id] = {
                "id": cat_id,
                "title": row[1],
                "notes": row[2],
                "index": row[3],
                "created_at": "2024-03-06T00:00:00Z",  # Default timestamp
                "updated_at": "2024-03-06T00:00:00Z",  # Default timestamp
                "clues": []
            }
        
        if row[4]:  # If there's a clue
            categories[cat_id]["clues"].append({
                "id": row[4],
                "value": row[5],
                "index": row[6],
                "question": row[7],
                "answer": row[8],
                "notes": row[9],
                "double": row[10],
                "created_at": "2024-03-06T00:00:00Z",  # Default timestamp
                "updated_at": "2024-03-06T00:00:00Z",  # Default timestamp
                "category_id": cat_id,
                "game_id": 0,  # Default value
                "invalid_count": 0  # Default value
            })
    
    conn.close()
    return list(categories.values())

def main():
    """Main function to export SQLite data to JSON files."""
    db_path = "jarchive/db.db"
    output_dir = Path("json_seasons")
    output_dir.mkdir(exist_ok=True)
    
    try:
        logger.info("Reading data from SQLite database...")
        categories = get_categories_with_clues(db_path)
        
        # Split categories into chunks of 1000 for manageable file sizes
        chunk_size = 1000
        for i in range(0, len(categories), chunk_size):
            chunk = categories[i:i + chunk_size]
            output_file = output_dir / f"chunk_{i//chunk_size + 1}.json"
            
            logger.info(f"Writing {len(chunk)} categories to {output_file}...")
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump({"categories": chunk}, f, indent=2, ensure_ascii=False)
            
        logger.info(f"Successfully exported {len(categories)} categories to {output_dir}")
        
    except Exception as e:
        logger.error(f"Error exporting data: {str(e)}")
        raise

if __name__ == "__main__":
    main() 