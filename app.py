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

# API Routes

@app.get("/")
def read_root():
    return {"message": "Welcome to jService API"}

@app.get("/api/random", response_model=List[dict])
def get_random(count: int = Query(1, ge=1, le=100)):
    """Get random clues, limited to 100 at a time"""
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
    
    query += " ORDER BY id LIMIT 100 OFFSET %s"
    params.append(offset)
    
    cursor.execute(query, params)
    clues = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return list(clues)

@app.get("/api/categories", response_model=List[dict])
def get_categories(count: int = Query(1, ge=1, le=100), offset: int = Query(0, ge=0)):
    """Get categories with pagination"""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    cursor.execute(
        """
        SELECT id, title, 
        (SELECT COUNT(*) FROM clues WHERE clues.category_id = categories.id) as clues_count 
        FROM categories 
        ORDER BY id
        LIMIT %s OFFSET %s
        """,
        (count, offset)
    )
    
    categories = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return list(categories)

@app.get("/api/category/{category_id}", response_model=dict)
def get_category(category_id: int):
    """Get a specific category by ID with its clues"""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    # Get category
    cursor.execute(
        "SELECT id, title FROM categories WHERE id = %s",
        (category_id,)
    )
    category = cursor.fetchone()
    
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # Get clues for this category
    cursor.execute(
        "SELECT * FROM clues WHERE category_id = %s AND invalid_count < 5",
        (category_id,)
    )
    clues = cursor.fetchall()
    
    # Get count of clues
    cursor.execute(
        "SELECT COUNT(*) as count FROM clues WHERE category_id = %s AND invalid_count < 5",
        (category_id,)
    )
    count = cursor.fetchone()["count"]
    
    cursor.close()
    conn.close()
    
    category["clues_count"] = count
    category["clues"] = list(clues)
    
    return category

@app.get("/api/final", response_model=List[dict])
def get_final(count: int = Query(1, ge=1, le=100)):
    """Get random final jeopardy clues"""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    cursor.execute(
        "SELECT * FROM clues WHERE value IS NULL ORDER BY RANDOM() LIMIT %s",
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
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "UPDATE clues SET invalid_count = invalid_count + 1 WHERE id = %s RETURNING id, invalid_count",
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