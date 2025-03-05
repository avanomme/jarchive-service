import psycopg2
import os
import random
import json

def get_db_connection():
    """Create a connection to the PostgreSQL database"""
    conn = psycopg2.connect(
        os.environ.get("DATABASE_URL", "postgresql://Adam@localhost:5432/jservice")
    )
    conn.autocommit = True
    return conn

def create_tables():
    """Create the necessary tables if they don't exist"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create categories table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS categories (
        id SERIAL PRIMARY KEY,
        title VARCHAR(255) NOT NULL
    )
    """)
    
    # Create clues table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS clues (
        id SERIAL PRIMARY KEY,
        answer TEXT NOT NULL,
        question TEXT NOT NULL,
        value INT,
        airdate DATE,
        category_id INT REFERENCES categories(id),
        game_id INT,
        invalid_count INT DEFAULT 0
    )
    """)
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print("Tables created successfully")

def insert_sample_data():
    """Insert sample data for testing"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if we already have data
    cursor.execute("SELECT COUNT(*) FROM categories")
    count = cursor.fetchone()[0]
    
    if count > 0:
        print(f"Database already contains {count} categories. Skipping sample data.")
        cursor.close()
        conn.close()
        return
    
    # Sample categories
    categories = [
        "U.S. History",
        "Science",
        "Movies",
        "Literature",
        "Geography",
        "Music",
        "Sports",
        "Mythology",
        "Food & Drink",
        "Technology"
    ]
    
    # Insert categories and keep track of their IDs
    category_ids = []
    for title in categories:
        cursor.execute(
            "INSERT INTO categories (title) VALUES (%s) RETURNING id",
            (title,)
        )
        category_id = cursor.fetchone()[0]
        category_ids.append(category_id)
    
    # Generate sample clues for each category
    for category_id in category_ids:
        # Get the category title
        cursor.execute("SELECT title FROM categories WHERE id = %s", (category_id,))
        category_title = cursor.fetchone()[0]
        
        # Create 10 clues for each category
        for i in range(10):
            value = random.choice([200, 400, 600, 800, 1000])
            
            # Generate question and answer based on category
            if category_title == "U.S. History":
                question = f"In {1700 + random.randint(50, 300)}, this person made a significant contribution to U.S. History."
                answer = f"Famous Person {i+1}"
            elif category_title == "Science":
                question = f"This scientific discovery in {1800 + random.randint(0, 220)} changed our understanding of the world."
                answer = f"Scientific Discovery {i+1}"
            else:
                question = f"Sample question {i+1} for {category_title}"
                answer = f"Sample answer {i+1} for {category_title}"
            
            cursor.execute(
                """
                INSERT INTO clues (answer, question, value, category_id, game_id, invalid_count, airdate) 
                VALUES (%s, %s, %s, %s, %s, %s, NOW())
                """,
                (answer, question, value, category_id, random.randint(1, 100), 0)
            )
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print("Sample data inserted successfully")

def check_tables_exist():
    """Check if the necessary tables exist"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT 1 FROM categories LIMIT 1")
        categories_exist = True
    except psycopg2.errors.UndefinedTable:
        categories_exist = False
    
    try:
        cursor.execute("SELECT 1 FROM clues LIMIT 1")
        clues_exist = True
    except psycopg2.errors.UndefinedTable:
        clues_exist = False
    
    cursor.close()
    conn.close()
    
    return categories_exist and clues_exist

if __name__ == "__main__":
    if check_tables_exist():
        print("Database tables already exist")
    else:
        print("Setting up database tables and sample data...")
        create_tables()
        insert_sample_data() 