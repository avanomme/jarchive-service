from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import random
import os
from dotenv import load_dotenv
from db_setup import Base, Category, Clue

# Load environment variables
load_dotenv()

app = FastAPI()

# Database setup
database_url = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/jservice')
edge_config_url = os.getenv('EDGE_CONFIG')

engine = create_engine(database_url)
SessionLocal = sessionmaker(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/api/category/{category_id}")
async def get_category(category_id: int):
    db = SessionLocal()
    try:
        category = db.query(Category).filter(Category.id == category_id).first()
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        
        # Get all clues for this category
        clues = db.query(Clue).filter(Clue.category_id == category_id).all()
        
        # Convert to dictionary format
        result = {
            "id": category.id,
            "title": category.title,
            "created_at": category.created_at.isoformat(),
            "updated_at": category.updated_at.isoformat(),
            "clues_count": category.clues_count,
            "clues": [
                {
                    "id": clue.id,
                    "answer": clue.answer,
                    "question": clue.question,
                    "value": clue.value,
                    "airdate": clue.airdate.isoformat(),
                    "category_id": clue.category_id,
                    "game_id": clue.game_id,
                    "invalid_count": clue.invalid_count,
                    "created_at": clue.created_at.isoformat(),
                    "updated_at": clue.updated_at.isoformat()
                }
                for clue in clues
            ]
        }
        return result
    finally:
        db.close()

@app.get("/api/random")
async def get_random_category():
    db = SessionLocal()
    try:
        # Get a random category ID
        category = db.query(Category).order_by(db.func.random()).first()
        if not category:
            raise HTTPException(status_code=404, detail="No categories found")
        
        return await get_category(category.id)
    finally:
        db.close()

@app.get("/api/categories")
async def get_categories():
    db = SessionLocal()
    try:
        categories = db.query(Category).all()
        return {
            "categories": [
                {
                    "id": cat.id,
                    "title": cat.title,
                    "created_at": cat.created_at.isoformat(),
                    "updated_at": cat.updated_at.isoformat(),
                    "clues_count": cat.clues_count
                }
                for cat in categories
            ]
        }
    finally:
        db.close()

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv('PORT', 8001))
    uvicorn.run(app, host="0.0.0.0", port=port) 