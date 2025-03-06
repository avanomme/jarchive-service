from fastapi import FastAPI, Query, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
from datetime import datetime
from supabase import create_client, Client
import os
from dotenv import load_dotenv
import random
import re  # Add import for regular expressions
import html  # Add import for HTML entity handling

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

# Protection bypass middleware
@app.middleware("http")
async def protection_bypass_middleware(request: Request, call_next):
    # Check for protection bypass header
    protection_bypass = request.headers.get("x-vercel-protection-bypass")
    if protection_bypass == "jserviceautobypasssecretcodekeys":
        # If bypass header is present, proceed with the request
        response = await call_next(request)
        return response
    else:
        # If no bypass header, return 403 Forbidden
        return Response(status_code=403, content="Authentication required")

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
        clues = clues[:count]
        
        # Transform the data to match the expected format
        if clues:
            first_clue = clues[0]
            category = first_clue['categories']
            return {
                "title": category['title'],
                "clues_count": len(clues),
                "clues": [
                    {
                        "answer": clue['answer'],
                        "question": clue['question']
                    }
                    for clue in clues
                ]
            }
        return {"title": "No Category", "clues_count": 0, "clues": []}
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
async def get_single_category(id: int):
    """Get a single category with all its clues."""
    try:
        # Get a random category ID from categories with enough clues
        category_response = supabase.table("categories") \
            .select("id") \
            .gte("clues_count", 4) \
            .execute()
        
        if not category_response.data:
            raise HTTPException(status_code=404, detail="No categories found with enough clues")
        
        # Select a random category ID
        random_category = random.choice(category_response.data)
        category_id = random_category["id"]
        
        # Get the specific category and its clues
        response = supabase.table("categories") \
            .select("*, clues(*)") \
            .eq("id", category_id) \
            .single() \
            .execute()
            
        if not response.data:
            raise HTTPException(status_code=404, detail="Category not found")
            
        category = response.data
        clues = category.get("clues", [])
            
        if clues and len(clues) >= 4:
            # Randomly select 4 clues from this category
            random.shuffle(clues)
            selected_clues = clues[:4]
            
            # Clean and format the clues
            formatted_clues = []
            for clue in selected_clues:
                # Get the question and answer
                question = clue.get("question", "").strip()
                answer = clue.get("answer", "").strip()
                
                # Remove HTML tags
                question = re.sub(r'<[^>]+>', '', question)
                answer = re.sub(r'<[^>]+>', '', answer)
                
                # Unescape HTML entities
                question = html.unescape(question)
                answer = html.unescape(answer)
                
                # Remove quotes and italics markers
                answer = answer.replace('"', '').replace("'", "").replace("<i>", "").replace("</i>", "")
                
                # If question is empty but answer isn't, swap them
                if not question and answer:
                    question = answer
                    # Try to extract a reasonable answer from the question
                    answer_parts = question.split(',')
                    if len(answer_parts) > 1:
                        answer = answer_parts[-1].strip()
                    else:
                        words = question.split()
                        if len(words) > 3:
                            answer = ' '.join(words[-3:]).strip()
                        else:
                            answer = question
                
                formatted_clues.append({
                    "answer": answer,
                    "question": question
                })
            
            # Format the response to match what the Flutter app expects
            return {
                "title": category["title"],
                "clues_count": len(formatted_clues),
                "clues": formatted_clues
            }
        else:
            raise HTTPException(status_code=404, detail="Could not find a category with enough clues")
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