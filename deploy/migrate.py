import os
import sqlite3
from supabase import create_client, Client
from dotenv import load_dotenv
import time
from datetime import datetime, timezone
import backoff

# Load environment variables
load_dotenv()

# Initialize Supabase client
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

def unix_to_iso(unix_timestamp):
    try:
        dt = datetime.fromtimestamp(unix_timestamp, tz=timezone.utc)
        return dt.isoformat()
    except:
        return datetime.now(timezone.utc).isoformat()

@backoff.on_exception(backoff.expo, Exception, max_tries=5)
def safe_supabase_operation(operation_func):
    """Execute a Supabase operation with retries"""
    return operation_func()

def process_remaining_categories(cursor, start_id=77500, chunk_size=100):
    # Get remaining categories with their clue counts
    cursor.execute("""
        SELECT c.id, c.name, COUNT(cl.id) as clues_count
        FROM categories c
        LEFT JOIN clues cl ON c.id = cl.category_id
        WHERE c.id > ?
        GROUP BY c.id, c.name
        ORDER BY c.id
    """, (start_id,))
    
    total_processed = start_id  # Start counting from where we left off
    while True:
        categories = []
        chunk = cursor.fetchmany(chunk_size)
        if not chunk:
            break
            
        for row in chunk:
            now = datetime.now(timezone.utc).isoformat()
            categories.append({
                'id': row[0],  # id
                'title': row[1],  # name
                'created_at': now,
                'updated_at': now,
                'clues_count': row[2]  # clues_count
            })
        
        if categories:
            try:
                safe_supabase_operation(
                    lambda: supabase.table('categories').upsert(categories).execute()
                )
                total_processed += len(categories)
                print(f"Inserted {len(categories)} categories (Total: {total_processed})")
            except Exception as e:
                print(f"Error inserting categories: {e}")
                time.sleep(5)  # Longer delay on error
            
        time.sleep(0.5)  # Reduced rate limiting

def process_clues(cursor, start_id=0, chunk_size=500):
    # Get clues joined with their categories and episodes for dates
    cursor.execute("""
        SELECT 
            cl.id,
            cl.question,
            cl.answer,
            cl.value,
            e.date,
            cl.category_id,
            b.episode_id
        FROM clues cl
        JOIN categories c ON cl.category_id = c.id
        JOIN boards b ON c.board_id = b.id
        JOIN episodes e ON b.episode_id = e.id
        WHERE cl.id > ? AND cl.question IS NOT NULL AND cl.answer IS NOT NULL
        ORDER BY cl.id
    """, (start_id,))
    
    total_processed = start_id
    while True:
        clues = []
        chunk = cursor.fetchmany(chunk_size)
        if not chunk:
            break
            
        for row in chunk:
            now = datetime.now(timezone.utc).isoformat()
            airdate = unix_to_iso(row[4]) if row[4] else now
            
            # Skip if question or answer is null
            if not row[1] or not row[2]:
                continue
                
            clues.append({
                'id': row[0],  # id
                'question': row[1] or "",  # question (default to empty string if null)
                'answer': row[2] or "",  # answer (default to empty string if null)
                'value': row[3] if row[3] is not None else 0,  # value
                'airdate': airdate,  # episode date
                'created_at': now,
                'updated_at': now,
                'category_id': row[5],  # category_id
                'game_id': row[6] if row[6] is not None else 0,  # episode_id as game_id
                'invalid_count': 0
            })
        
        if clues:
            try:
                safe_supabase_operation(
                    lambda: supabase.table('clues').upsert(clues).execute()
                )
                total_processed += len(clues)
                print(f"Inserted {len(clues)} clues (Total: {total_processed})")
            except Exception as e:
                print(f"Error inserting clues: {e}")
                time.sleep(5)  # Longer delay on error
            
        time.sleep(0.5)  # Reduced rate limiting

def process_final_clues(cursor, chunk_size=500):
    # Get final clues and create categories for them
    cursor.execute("""
        SELECT * FROM final_clues 
        WHERE question IS NOT NULL AND answer IS NOT NULL
    """)
    
    total_processed = 0
    while True:
        finals = []
        categories = []
        chunk = cursor.fetchmany(chunk_size)
        if not chunk:
            break
            
        for row in chunk:
            now = datetime.now(timezone.utc).isoformat()
            
            # Skip if question or answer is null
            if not row[3] or not row[4]:
                continue
                
            # Prepare both category and clue for batch insert
            categories.append({
                'id': 1000000 + row[0],  # Use high numbers to avoid conflicts
                'title': row[1] or "Final Jeopardy",  # category (default if null)
                'created_at': now,
                'updated_at': now,
                'clues_count': 1
            })
            
            finals.append({
                'id': 1000000 + row[0],  # Use high numbers to avoid conflicts
                'question': row[3] or "",  # question (default to empty string if null)
                'answer': row[4] or "",  # answer (default to empty string if null)
                'value': 0,  # Final clues don't have values
                'airdate': now,
                'created_at': now,
                'updated_at': now,
                'category_id': 1000000 + row[0],
                'game_id': 0,
                'invalid_count': 0
            })
        
        if categories:
            try:
                # Batch insert categories
                safe_supabase_operation(
                    lambda: supabase.table('categories').upsert(categories).execute()
                )
                print(f"Inserted {len(categories)} final categories (Total: {total_processed + len(categories)})")
            except Exception as e:
                print(f"Error inserting final categories: {e}")
                time.sleep(5)  # Longer delay on error
        
        if finals:
            try:
                # Batch insert clues
                safe_supabase_operation(
                    lambda: supabase.table('clues').upsert(finals).execute()
                )
                total_processed += len(finals)
                print(f"Inserted {len(finals)} final clues (Total: {total_processed})")
            except Exception as e:
                print(f"Error inserting final clues: {e}")
                time.sleep(5)  # Longer delay on error
            
        time.sleep(0.5)  # Reduced rate limiting

def main():
    # Connect to SQLite database
    conn = sqlite3.connect('../jarchive/db.db')
    cursor = conn.cursor()
    
    print("Processing remaining categories...")
    process_remaining_categories(cursor)
    
    print("Processing clues...")
    process_clues(cursor, start_id=3800)  # Start from where we left off
    
    print("Processing final clues...")
    process_final_clues(cursor)
    
    conn.close()
    print("Migration complete")

if __name__ == "__main__":
    main() 