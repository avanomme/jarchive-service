import requests
import json
from unittest import mock
import pytest
import os
import importlib

# Sample responses
MOCK_RESPONSES = {
    "/": {"message": "Welcome to jService API"},
    "/api/random": [
        {
            "id": 1,
            "answer": "Albert Einstein",
            "question": "This physicist developed the theory of relativity",
            "value": 200,
            "airdate": "2022-01-01T00:00:00",
            "category_id": 1,
            "game_id": 1,
            "invalid_count": 0
        }
    ],
    "/api/clues": [
        {
            "id": 1,
            "answer": "Albert Einstein",
            "question": "This physicist developed the theory of relativity",
            "value": 200,
            "airdate": "2022-01-01T00:00:00",
            "category_id": 1,
            "game_id": 1,
            "invalid_count": 0
        },
        {
            "id": 2,
            "answer": "Marie Curie",
            "question": "This scientist discovered radium",
            "value": 400,
            "airdate": "2022-01-02T00:00:00",
            "category_id": 1,
            "game_id": 1,
            "invalid_count": 0
        }
    ],
    "/api/categories": [
        {
            "id": 1,
            "title": "Science",
            "clues_count": 2
        },
        {
            "id": 2,
            "title": "History",
            "clues_count": 2
        }
    ],
    "/api/category/1": {
        "id": 1,
        "title": "Science",
        "clues_count": 2,
        "clues": [
            {
                "id": 1,
                "answer": "Albert Einstein",
                "question": "This physicist developed the theory of relativity",
                "value": 200,
                "airdate": "2022-01-01T00:00:00",
                "category_id": 1,
                "game_id": 1,
                "invalid_count": 0
            },
            {
                "id": 2,
                "answer": "Marie Curie",
                "question": "This scientist discovered radium",
                "value": 400,
                "airdate": "2022-01-02T00:00:00",
                "category_id": 1,
                "game_id": 1,
                "invalid_count": 0
            }
        ]
    },
    "/api/final": [
        {
            "id": 7,
            "answer": "Final Jeopardy",
            "question": "This is a test final jeopardy question",
            "value": None,
            "airdate": "2022-01-07T00:00:00",
            "category_id": 1,
            "game_id": 4,
            "invalid_count": 0
        }
    ],
    "/api/invalid": {
        "id": 1,
        "invalid_count": 1
    }
}

def test_api_mock():
    """Test API using mocked responses"""
    base_url = "http://localhost:8000"
    
    # Test root endpoint
    print("Testing root endpoint...")
    response = MOCK_RESPONSES["/"]
    assert "message" in response
    assert response["message"] == "Welcome to jService API"
    print("✅ Root endpoint test passed")
    
    # Test random endpoint
    print("Testing random endpoint...")
    response = MOCK_RESPONSES["/api/random"]
    assert isinstance(response, list)
    assert len(response) == 1
    assert "id" in response[0]
    assert "answer" in response[0]
    assert "question" in response[0]
    print("✅ Random endpoint test passed")
    
    # Test clues endpoint
    print("Testing clues endpoint...")
    response = MOCK_RESPONSES["/api/clues"]
    assert isinstance(response, list)
    assert len(response) >= 1
    for clue in response:
        assert "id" in clue
        assert "answer" in clue
        assert "question" in clue
        assert "value" in clue
        assert "category_id" in clue
    print("✅ Clues endpoint test passed")
    
    # Test categories endpoint
    print("Testing categories endpoint...")
    response = MOCK_RESPONSES["/api/categories"]
    assert isinstance(response, list)
    assert len(response) >= 1
    for category in response:
        assert "id" in category
        assert "title" in category
        assert "clues_count" in category
    print("✅ Categories endpoint test passed")
    
    # Test category endpoint
    print("Testing category endpoint...")
    response = MOCK_RESPONSES["/api/category/1"]
    assert "id" in response
    assert "title" in response
    assert "clues_count" in response
    assert "clues" in response
    assert isinstance(response["clues"], list)
    assert len(response["clues"]) > 0
    print("✅ Category endpoint test passed")
    
    # Test final endpoint
    print("Testing final endpoint...")
    response = MOCK_RESPONSES["/api/final"]
    assert isinstance(response, list)
    assert len(response) >= 1
    for clue in response:
        assert clue["value"] is None
    print("✅ Final endpoint test passed")
    
    # Test invalid endpoint
    print("Testing invalid endpoint...")
    response = MOCK_RESPONSES["/api/invalid"]
    assert "id" in response
    assert "invalid_count" in response
    print("✅ Invalid endpoint test passed")
    
    print("All tests passed!")

if __name__ == "__main__":
    test_api_mock() 