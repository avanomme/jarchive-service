import pytest
from fastapi.testclient import TestClient
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os
import tempfile
import time
from app import app

# Create a test client
client = TestClient(app)

# Test configuration
DB_NAME = "jservice_test"
DB_USER = "postgres"
DB_PASSWORD = "postgres"
DB_HOST = "localhost"
DB_PORT = "5432"

# Global variables for test database
TEST_DB_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

def setup_test_db():
    """Set up a test database with mock data"""
    try:
        # Connect to PostgreSQL server
        conn = psycopg2.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Drop database if it exists
        cursor.execute(f"DROP DATABASE IF EXISTS {DB_NAME}")
        
        # Create database
        cursor.execute(f"CREATE DATABASE {DB_NAME}")
        cursor.close()
        conn.close()
        
        # Connect to the test database
        conn = psycopg2.connect(TEST_DB_URL)
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute("""
            CREATE TABLE categories (
                id SERIAL PRIMARY KEY,
                title VARCHAR(255) NOT NULL
            )
        """)
        
        cursor.execute("""
            CREATE TABLE clues (
                id SERIAL PRIMARY KEY,
                answer VARCHAR(255) NOT NULL,
                question TEXT NOT NULL,
                value INTEGER,
                airdate TIMESTAMP,
                category_id INTEGER REFERENCES categories(id),
                game_id INTEGER,
                invalid_count INTEGER DEFAULT 0
            )
        """)
        
        # Insert test data
        # Categories
        cursor.execute("INSERT INTO categories (id, title) VALUES (1, 'Science')")
        cursor.execute("INSERT INTO categories (id, title) VALUES (2, 'History')")
        cursor.execute("INSERT INTO categories (id, title) VALUES (3, 'Geography')")
        
        # Clues
        cursor.execute("""
            INSERT INTO clues (id, answer, question, value, airdate, category_id, game_id, invalid_count)
            VALUES 
            (1, 'Albert Einstein', 'This physicist developed the theory of relativity', 200, '2022-01-01', 1, 1, 0),
            (2, 'Marie Curie', 'This scientist discovered radium', 400, '2022-01-02', 1, 1, 0),
            (3, 'Abraham Lincoln', 'This president delivered the Gettysburg Address', 200, '2022-01-03', 2, 2, 0),
            (4, 'George Washington', 'This was the first U.S. president', 400, '2022-01-04', 2, 2, 0),
            (5, 'The Amazon', 'This is the largest river by volume', 200, '2022-01-05', 3, 3, 0),
            (6, 'The Sahara', 'This is the largest hot desert', 400, '2022-01-06', 3, 3, 0),
            (7, 'Final Jeopardy', 'This is a test final jeopardy question', NULL, '2022-01-07', 1, 4, 0)
        """)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        # Set environment variable for the test
        os.environ["DATABASE_URL"] = TEST_DB_URL
        
        return True
    except Exception as e:
        print(f"Error setting up test database: {e}")
        return False

def test_root():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to jService API"}

def test_random():
    """Test random endpoint"""
    response = client.get("/api/random")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) == 1
    
    # Test with count parameter
    response = client.get("/api/random?count=3")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) == 3

def test_clues():
    """Test clues endpoint"""
    # Test without filters
    response = client.get("/api/clues")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    
    # Test with value filter
    response = client.get("/api/clues?value=200")
    assert response.status_code == 200
    for clue in response.json():
        assert clue["value"] == 200
    
    # Test with category filter
    response = client.get("/api/clues?category=1")
    assert response.status_code == 200
    for clue in response.json():
        assert clue["category_id"] == 1
    
    # Test with offset
    response = client.get("/api/clues?offset=2")
    assert response.status_code == 200

def test_categories():
    """Test categories endpoint"""
    # Test default
    response = client.get("/api/categories")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) == 1
    
    # Test with count parameter
    response = client.get("/api/categories?count=3")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) == 3
    
    # Test with offset
    response = client.get("/api/categories?offset=1")
    assert response.status_code == 200

def test_category():
    """Test category endpoint"""
    # Test with valid category ID
    response = client.get("/api/category/1")
    assert response.status_code == 200
    assert response.json()["id"] == 1
    assert response.json()["title"] == "Science"
    assert "clues" in response.json()
    assert "clues_count" in response.json()
    
    # Test with invalid category ID
    response = client.get("/api/category/999")
    assert response.status_code == 404

def test_final():
    """Test final endpoint"""
    response = client.get("/api/final")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    for clue in response.json():
        assert clue["value"] is None

def test_invalid():
    """Test invalid endpoint"""
    # Test marking a clue as invalid
    response = client.post("/api/invalid", json={"id": 1})
    assert response.status_code == 200
    assert response.json()["id"] == 1
    assert response.json()["invalid_count"] == 1
    
    # Test with invalid clue ID
    response = client.post("/api/invalid", json={"id": 999})
    assert response.status_code == 404

def run_tests():
    """Run all tests"""
    # Setup test database
    if not setup_test_db():
        print("Failed to set up test database. Tests will not run.")
        return
    
    # Run tests
    print("Testing root endpoint...")
    test_root()
    print("✅ Root endpoint test passed")
    
    print("Testing random endpoint...")
    test_random()
    print("✅ Random endpoint test passed")
    
    print("Testing clues endpoint...")
    test_clues()
    print("✅ Clues endpoint test passed")
    
    print("Testing categories endpoint...")
    test_categories()
    print("✅ Categories endpoint test passed")
    
    print("Testing category endpoint...")
    test_category()
    print("✅ Category endpoint test passed")
    
    print("Testing final endpoint...")
    test_final()
    print("✅ Final endpoint test passed")
    
    print("Testing invalid endpoint...")
    test_invalid()
    print("✅ Invalid endpoint test passed")
    
    print("All tests passed!")

if __name__ == "__main__":
    run_tests() 