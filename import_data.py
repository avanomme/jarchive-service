import psycopg2
import csv
import os
import sys
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from datetime import datetime

def import_data(tsv_file, db_url=None):
    """Import jService data from a TSV file into PostgreSQL"""
    if db_url is None:
        db_url = os.environ.get("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/jservice")
    
    print(f"Connecting to database: {db_url}")
    
    try:
        # Connect to the database
        conn = psycopg2.connect(db_url)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Drop existing tables if they exist
        print("Dropping existing tables...")
        cursor.execute("DROP TABLE IF EXISTS clues")
        cursor.execute("DROP TABLE IF EXISTS categories")
        
        # Create tables
        print("Creating tables...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS clues (
                id SERIAL PRIMARY KEY,
                answer TEXT NOT NULL,
                question TEXT NOT NULL,
                value INTEGER,
                airdate TIMESTAMP,
                category_id INTEGER REFERENCES categories(id),
                game_id INTEGER,
                invalid_count INTEGER DEFAULT 0
            )
        """)
        
        # Load data from TSV file
        print(f"Loading data from {tsv_file}...")
        
        # Expected TSV format: game_id, airdate, round, value, category, clue, response
        categories = {}
        clues = []
        category_id_counter = 1
        clue_id_counter = 1
        
        with open(tsv_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter='\t')
            header = next(reader)  # Skip header row
            
            for row in reader:
                if len(row) < 7:
                    continue  # Skip incomplete rows
                
                game_id = int(row[0]) if row[0].isdigit() else None
                airdate_str = row[1].strip()
                # Convert airdate to proper format (assuming MM/DD/YYYY)
                try:
                    if airdate_str:
                        airdate = datetime.strptime(airdate_str, '%m/%d/%Y')
                    else:
                        airdate = None
                except ValueError:
                    airdate = None
                
                value_str = row[3].strip().replace('$', '').replace(',', '')
                value = int(value_str) if value_str.isdigit() else None
                
                category_title = row[4].strip()
                question = row[5].strip()
                answer = row[6].strip()
                
                # Get or create category ID
                if category_title not in categories:
                    categories[category_title] = category_id_counter
                    category_id_counter += 1
                
                category_id = categories[category_title]
                
                # Add clue
                clues.append({
                    'id': clue_id_counter,
                    'game_id': game_id,
                    'airdate': airdate,
                    'value': value,
                    'category_id': category_id,
                    'question': question,
                    'answer': answer
                })
                
                clue_id_counter += 1
        
        # Insert categories
        print(f"Importing {len(categories)} categories...")
        for title, category_id in categories.items():
            cursor.execute(
                "INSERT INTO categories (id, title) VALUES (%s, %s) ON CONFLICT (id) DO NOTHING",
                (category_id, title)
            )
        
        # Insert clues
        print(f"Importing {len(clues)} clues...")
        for i, clue in enumerate(clues):
            cursor.execute(
                """
                INSERT INTO clues (id, answer, question, value, airdate, category_id, game_id, invalid_count)
                VALUES (%s, %s, %s, %s, %s, %s, %s, 0)
                ON CONFLICT (id) DO NOTHING
                """,
                (
                    clue['id'],
                    clue['answer'],
                    clue['question'],
                    clue['value'],
                    clue['airdate'],
                    clue['category_id'],
                    clue['game_id']
                )
            )
            
            # Print progress
            if (i + 1) % 1000 == 0:
                print(f"Imported {i + 1} of {len(clues)} clues...")
        
        # Close connection
        cursor.close()
        conn.close()
        
        print("Import completed successfully!")
        return True
        
    except Exception as e:
        print(f"Error importing data: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python import_data.py <tsv_file> [database_url]")
        sys.exit(1)
    
    tsv_file = sys.argv[1]
    db_url = sys.argv[2] if len(sys.argv) > 2 else None
    
    if import_data(tsv_file, db_url):
        print("Data import completed successfully!")
    else:
        print("Data import failed.")
        sys.exit(1) 