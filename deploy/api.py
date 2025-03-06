from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
from datetime import datetime
from supabase import create_client, Client
import os
from dotenv import load_dotenv
import random

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="jService API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Supabase client
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

@app.get("/api/random")
async def get_random_clues(count: Optional[int] = Query(1, le=100)):
    """Get random clues with their categories."""
    try:
        # Get random clues with their categories
        response = supabase.table("clues").select("*, categories(*)").limit(count).execute()
        clues = response.data
        
        # Randomize the results
        random.shuffle(clues)
        return clues[:count]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/final")
async def get_final_clues(count: Optional[int] = Query(1, le=100)):
    """Get random final jeopardy clues."""
    try:
        # Get clues with null value (final jeopardy) and their categories
        response = supabase.table("clues").select("*, categories(*)").is_("value", "null").limit(count).execute()
        clues = response.data
        
        # Randomize the results
        random.shuffle(clues)
        return clues[:count]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/clues")
async def get_clues(
    value: Optional[int] = None,
    min_date: Optional[str] = None,
    max_date: Optional[str] = None,
    game_id: Optional[int] = None,
    category: Optional[int] = None,
    offset: Optional[int] = 0
):
    """Get clues with optional filters."""
    try:
        query = supabase.table("clues").select("*, categories(*)")
        
        # Apply filters
        if value is not None:
            query = query.eq("value", value)
        if min_date:
            query = query.gte("airdate", min_date)
        if max_date:
            query = query.lte("airdate", max_date)
        if game_id:
            query = query.eq("game_id", game_id)
        if category:
            query = query.eq("category_id", category)
            
        # Add pagination
        query = query.range(offset, offset + 99)
        
        response = query.execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/categories")
async def get_categories(
    offset: Optional[int] = 0,
    count: Optional[int] = Query(1, le=100)
):
    """Get categories with pagination."""
    try:
        response = supabase.table("categories").select("*").range(offset, offset + count - 1).execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/category")
async def get_single_category(category_id: int):
    """Get a single category with all its clues."""
    try:
        # Get category with all its clues
        response = supabase.table("categories").select("*, clues(*)").eq("id", category_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Category not found")
            
        category = response.data[0]
        
        # Remove created_at and updated_at from clues
        if "clues" in category:
            for clue in category["clues"]:
                clue.pop("created_at", None)
                clue.pop("updated_at", None)
                
        return category
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/mark_invalid")
async def mark_clue_invalid(clue_id: int):
    """Mark a clue as invalid by incrementing its invalid_count."""
    try:
        # Get current invalid_count
        response = supabase.table("clues").select("invalid_count").eq("id", clue_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Clue not found")
            
        current_count = response.data[0]["invalid_count"] or 0
        
        # Update invalid_count
        response = supabase.table("clues").update({"invalid_count": current_count + 1}).eq("id", clue_id).execute()
        
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 