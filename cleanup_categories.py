import psycopg2
import re
import os

def get_db_connection():
    conn = psycopg2.connect(
        os.environ.get("DATABASE_URL", "postgresql://Adam@localhost:5432/jservice")
    )
    conn.autocommit = True
    return conn

def clean_category_title(title):
    if not title:
        return "UNKNOWN"
    
    # Remove Alex comments
    if "(Alex:" in title or "Alex:" in title:
        # Try to extract the actual category name if in quotes
        match = re.search(r'"([^"]+)"', title)
        if match:
            return match.group(1)
        
        # Try to find text that might be the category name
        match = re.search(r'have\s+\"([^\"]+)\"', title)
        if match:
            return match.group(1)
            
        # Another pattern: we have categories like...
        match = re.search(r'category\s+(?:called|named)\s+([A-Z]+)', title)
        if match:
            return match.group(1)
            
        # If no quotes found, remove the Alex comment completely
        return "UNKNOWN"
    
    return title

def cleanup_categories():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get all category IDs and titles
    cursor.execute("SELECT id, title FROM categories")
    categories = cursor.fetchall()
    
    print(f"Found {len(categories)} categories to process")
    count_changed = 0
    count_unknown = 0
    
    # Process each category
    for category_id, title in categories:
        cleaned_title = clean_category_title(title)
        
        if cleaned_title != title:
            count_changed += 1
            if cleaned_title == "UNKNOWN":
                count_unknown += 1
                
            # Update the category title
            cursor.execute(
                "UPDATE categories SET title = %s WHERE id = %s",
                (cleaned_title, category_id)
            )
            print(f"Updated category {category_id}: '{title}' -> '{cleaned_title}'")
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print(f"Cleanup complete. Modified {count_changed} categories. {count_unknown} set to UNKNOWN.")

if __name__ == "__main__":
    cleanup_categories() 