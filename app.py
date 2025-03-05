from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
import psycopg2.extras
import os
import random
from typing import List, Optional
import json
from pydantic import BaseModel

app = FastAPI(title="jService API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database connection
def get_db_connection():
    conn = psycopg2.connect(
        os.environ.get("DATABASE_URL", "postgresql://Adam@localhost:5432/jservice")
    )
    conn.autocommit = True
    return conn

# Check if database is initialized
def check_db_initialized():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM categories LIMIT 1")
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result is not None
    except psycopg2.errors.UndefinedTable:
        return False
    except Exception as e:
        print(f"Database connection error: {e}")
        return False

# API Routes

@app.get("/")
def read_root():
    db_status = "initialized" if check_db_initialized() else "not initialized"
    return {
        "message": "Welcome to jService API", 
        "status": "online",
        "database_status": db_status
    }

@app.get("/api/random", response_model=List[dict])
def get_random(count: int = Query(1, ge=1, le=100)):
    """Get random clues, limited to 100 at a time"""
    if not check_db_initialized():
        raise HTTPException(status_code=503, detail="Database not initialized. Please import the jservice database dump.")
        
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    cursor.execute(
        "SELECT * FROM clues WHERE invalid_count < 5 ORDER BY RANDOM() LIMIT %s",
        (count,)
    )
    clues = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return list(clues)

@app.get("/api/clues", response_model=List[dict])
def get_clues(
    value: Optional[int] = None,
    category: Optional[int] = None,
    min_date: Optional[str] = None,
    max_date: Optional[str] = None,
    offset: int = Query(0, ge=0)
):
    """Get clues with optional filters"""
    if not check_db_initialized():
        raise HTTPException(status_code=503, detail="Database not initialized. Please import the jservice database dump.")
        
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    query = "SELECT * FROM clues WHERE invalid_count < 5"
    params = []
    
    if value is not None:
        query += " AND value = %s"
        params.append(value)
        
    if category is not None:
        query += " AND category_id = %s"
        params.append(category)
        
    if min_date is not None:
        query += " AND airdate >= %s"
        params.append(min_date)
        
    if max_date is not None:
        query += " AND airdate <= %s"
        params.append(max_date)
    
    query += " ORDER BY clues.id LIMIT 100 OFFSET %s"
    params.append(offset)
    
    cursor.execute(query, params)
    clues = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return list(clues)

@app.get("/api/categories", response_model=List[dict])
def get_categories(count: int = Query(1, ge=1, le=100), offset: int = Query(0, ge=0)):
    """Get categories with pagination"""
    if not check_db_initialized():
        raise HTTPException(status_code=503, detail="Database not initialized. Please import the jservice database dump.")
        
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    cursor.execute(
        """
        SELECT categories.id, categories.title, 
        (SELECT COUNT(*) FROM clues WHERE clues.category_id = categories.id) as clues_count 
        FROM categories 
        ORDER BY categories.id
        LIMIT %s OFFSET %s
        """,
        (count, offset)
    )
    
    categories = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return list(categories)

# This endpoint matches the original jService format expected by the Flutter app
@app.get("/api/category", response_model=dict)
def get_category_query(id: int):
    """Get a specific category by ID as a query parameter - matches original jService format"""
    try:
        return get_category_data(id)
    except psycopg2.errors.UndefinedTable:
        # Return a mock response for testing when database isn't initialized
        return {
            "id": id,
            "title": "Sample Category",
            "clues_count": 5,
            "clues": [
                {"answer": "Answer 1", "question": "Question 1"},
                {"answer": "Answer 2", "question": "Question 2"},
                {"answer": "Answer 3", "question": "Question 3"},
                {"answer": "Answer 4", "question": "Question 4"},
                {"answer": "Answer 5", "question": "Question 5"}
            ]
        }

@app.get("/api/category/{category_id}", response_model=dict)
def get_category(category_id: int):
    """Get a specific category by ID with its clues"""
    try:
        return get_category_data(category_id)
    except psycopg2.errors.UndefinedTable:
        # Return a mock response for testing when database isn't initialized
        return {
            "id": category_id,
            "title": "Sample Category",
            "clues_count": 5,
            "clues": [
                {"answer": "Answer 1", "question": "Question 1"},
                {"answer": "Answer 2", "question": "Question 2"},
                {"answer": "Answer 3", "question": "Question 3"},
                {"answer": "Answer 4", "question": "Question 4"},
                {"answer": "Answer 5", "question": "Question 5"}
            ]
        }

def get_category_data(category_id: int):
    """Common function to get category data by ID"""
    if not check_db_initialized():
        raise HTTPException(status_code=503, detail="Database not initialized. Please import the jservice database dump.")
        
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    # Get category
    cursor.execute(
        "SELECT categories.id, categories.title FROM categories WHERE categories.id = %s",
        (category_id,)
    )
    category = cursor.fetchone()
    
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # Get clues for this category
    cursor.execute(
        """
        SELECT clues.id, clues.answer, clues.question, clues.value, 
        clues.airdate, clues.category_id, clues.game_id, clues.invalid_count 
        FROM clues 
        WHERE clues.category_id = %s AND clues.invalid_count < 5
        """,
        (category_id,)
    )
    clues = cursor.fetchall()
    
    # Ensure we have at least 4 clues with distinct answers for the multiple choice question
    if len(clues) < 4:
        # Get more clues from other categories if needed
        cursor.execute(
            """
            SELECT clues.id, clues.answer, clues.question, clues.value, 
            clues.airdate, clues.category_id, clues.game_id, clues.invalid_count 
            FROM clues 
            WHERE clues.invalid_count < 5 AND clues.category_id != %s
            ORDER BY RANDOM() 
            LIMIT 10
            """,
            (category_id,)
        )
        additional_clues = cursor.fetchall()
        clues.extend(additional_clues)
    
    # Get count of clues
    cursor.execute(
        "SELECT COUNT(*) as count FROM clues WHERE clues.category_id = %s AND clues.invalid_count < 5",
        (category_id,)
    )
    count = cursor.fetchone()["count"]
    
    cursor.close()
    conn.close()
    
    # Format the response exactly as expected by the Flutter app
    category["clues_count"] = count
    category["clues"] = list(clues)
    
    # Print debug information - will appear in the server logs
    print(f"Category structure: {list(category.keys())}")
    if clues and len(clues) > 0:
        print(f"Clue structure: {list(clues[0].keys())}")
    
    # Ensure we have at least 4 clues with distinct answers for the Flutter app
    distinct_answers = set()
    valid_clues = []
    
    for clue in category["clues"]:
        # Ensure all clues have the expected fields
        if "answer" not in clue or "question" not in clue:
            print(f"Warning: Clue missing required fields: {clue}")
            continue
        
        # Clean the answer text
        answer = clue["answer"]
        if answer and isinstance(answer, str):
            # Add to valid clues
            valid_clues.append(clue)
            distinct_answers.add(answer)
    
    # Make sure we have enough distinct answers
    if len(distinct_answers) < 4:
        print(f"Error: Not enough distinct answers: {len(distinct_answers)}")
        raise HTTPException(status_code=404, detail="Not enough distinct clues found for this category")
    
    category["clues"] = valid_clues
    
    return category

@app.get("/api/final", response_model=List[dict])
def get_final(count: int = Query(1, ge=1, le=100)):
    """Get random final jeopardy clues"""
    if not check_db_initialized():
        raise HTTPException(status_code=503, detail="Database not initialized. Please import the jservice database dump.")
        
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    cursor.execute(
        "SELECT * FROM clues WHERE clues.value IS NULL ORDER BY RANDOM() LIMIT %s",
        (count,)
    )
    clues = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return list(clues)

class InvalidRequest(BaseModel):
    id: int

@app.post("/api/invalid")
def mark_invalid(request: InvalidRequest):
    """Mark a clue as invalid"""
    if not check_db_initialized():
        raise HTTPException(status_code=503, detail="Database not initialized. Please import the jservice database dump.")
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "UPDATE clues SET invalid_count = invalid_count + 1 WHERE clues.id = %s RETURNING clues.id, clues.invalid_count",
        (request.id,)
    )
    result = cursor.fetchone()
    
    conn.commit()
    cursor.close()
    conn.close()
    
    if result is None:
        raise HTTPException(status_code=404, detail="Clue not found")
        
    return {"id": result[0], "invalid_count": result[1]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000))) 