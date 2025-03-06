from fastapi import FastAPI, HTTPException
import json
from typing import Dict, List, Optional
import random

app = FastAPI()

# Load data once at startup
with open('jservice_data.json', 'r') as f:
    data = json.load(f)

# Create efficient lookup structures
categories_by_id: Dict[int, dict] = {cat['id']: cat for cat in data['categories']}
clues_by_category: Dict[int, List[dict]] = {}

# Organize clues by category_id for efficient lookup
for clue in data['all_clues']:
    if clue['category_id'] not in clues_by_category:
        clues_by_category[clue['category_id']] = []
    clues_by_category[clue['category_id']].append(clue)

@app.get("/api/category/{category_id}")
async def get_category(category_id: int):
    try:
        category_id = int(category_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Category ID must be a number")
        
    if category_id not in categories_by_id:
        raise HTTPException(status_code=404, detail="Category not found")
    
    category = categories_by_id[category_id].copy()
    category['clues'] = clues_by_category.get(category_id, [])
    return category

@app.get("/api/random")
async def get_random_category():
    category_id = random.choice(list(categories_by_id.keys()))
    return await get_category(category_id)

@app.get("/api/categories")
async def get_categories():
    return {"categories": list(categories_by_id.values())}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)  # Changed port to 8001 