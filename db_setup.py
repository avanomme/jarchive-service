from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import os
import csv
from datetime import datetime, timezone
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

Base = declarative_base()

class Category(Base):
    __tablename__ = 'categories'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=False)
    clues_count = Column(Integer, nullable=False, default=0)
    clues = relationship("Clue", back_populates="category")

class Clue(Base):
    __tablename__ = 'clues'
    
    id = Column(Integer, primary_key=True)
    answer = Column(Text, nullable=False)
    question = Column(Text, nullable=False)
    value = Column(Integer)
    airdate = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=False)
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=False)
    game_id = Column(Integer)
    invalid_count = Column(Integer)
    
    category = relationship("Category", back_populates="clues")

def setup_database(database_url):
    logger.info("Starting database setup...")
    
    # Create engine and tables
    engine = create_engine(database_url)
    logger.info("Database engine created")
    
    # Create tables if they don't exist
    Base.metadata.create_all(engine)
    logger.info("Database tables created")
    
    # Create session
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Check if we already have data
        category_count = session.query(Category).count()
        if category_count > 0:
            logger.info(f"Database already populated with {category_count} categories, skipping import.")
            return
        
        logger.info("Starting data import...")
        # Store categories with their clues
        categories = {}
        category_counter = 1
        clue_counter = 1
        current_date = datetime.now(timezone.utc)
        
        # First pass: Create categories
        with open('combined_season1-40.tsv', 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file, delimiter='\t')
            for row in reader:
                category_title = row['category'].strip()
                if category_title not in categories:
                    category = Category(
                        id=category_counter,
                        title=category_title,
                        created_at=current_date,
                        updated_at=current_date,
                        clues_count=0
                    )
                    categories[category_title] = category
                    session.add(category)
                    category_counter += 1
        
        # Commit categories to get their IDs
        session.commit()
        logger.info(f"Created {len(categories)} categories")
        
        # Second pass: Create clues and update category counts
        category_clue_counts = {}
        with open('combined_season1-40.tsv', 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file, delimiter='\t')
            for row in reader:
                category_title = row['category'].strip()
                category = categories[category_title]
                
                # Create clue
                clue = Clue(
                    id=clue_counter,
                    answer=row['answer'].strip(),
                    question=row['comments'].strip(),
                    value=int(row['clue_value']) if row['clue_value'].isdigit() else 200,
                    airdate=datetime.strptime(row['air_date'] + "T00:00:00.000Z", "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc),
                    created_at=current_date,
                    updated_at=current_date,
                    category_id=category.id,
                    game_id=clue_counter,
                    invalid_count=None
                )
                session.add(clue)
                
                # Update category clue count
                if category.id not in category_clue_counts:
                    category_clue_counts[category.id] = 0
                category_clue_counts[category.id] += 1
                
                clue_counter += 1
                
                # Commit every 1000 clues to avoid memory issues
                if clue_counter % 1000 == 0:
                    session.commit()
                    logger.info(f"Imported {clue_counter} clues")
        
        # Update category clue counts and remove categories with less than 5 clues
        for category in categories.values():
            count = category_clue_counts.get(category.id, 0)
            if count < 5:
                session.delete(category)
            else:
                category.clues_count = count
        
        # Final commit
        session.commit()
        logger.info(f"Database setup completed successfully! Imported {len(categories)} categories and {clue_counter} clues")
        
    except Exception as e:
        logger.error(f"Error during database setup: {str(e)}")
        session.rollback()
        raise
    finally:
        session.close()

if __name__ == "__main__":
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        raise ValueError("DATABASE_URL environment variable is not set")
    setup_database(database_url) 