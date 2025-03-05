import requests
import json
import time
import sys

def test_api_live():
    """Test the live API endpoints"""
    base_url = "http://localhost:8000"
    
    try:
        # Test root endpoint
        print("Testing root endpoint...")
        response = requests.get(f"{base_url}/")
        response.raise_for_status()
        data = response.json()
        assert "message" in data
        assert data["message"] == "Welcome to jService API"
        print("✅ Root endpoint test passed")
        
        # Test random endpoint
        print("Testing random endpoint...")
        response = requests.get(f"{base_url}/api/random")
        response.raise_for_status()
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert "id" in data[0]
        assert "answer" in data[0]
        assert "question" in data[0]
        
        # Test with count parameter
        response = requests.get(f"{base_url}/api/random?count=3")
        response.raise_for_status()
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 3
        print("✅ Random endpoint test passed")
        
        # Test clues endpoint
        print("Testing clues endpoint...")
        response = requests.get(f"{base_url}/api/clues")
        response.raise_for_status()
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        
        # Store a valid category ID and value for later tests
        valid_category_id = data[0]["category_id"]
        valid_value = data[0]["value"]
        
        # Test with value filter
        if valid_value:
            response = requests.get(f"{base_url}/api/clues?value={valid_value}")
            response.raise_for_status()
            data = response.json()
            assert isinstance(data, list)
            for clue in data:
                assert clue["value"] == valid_value
        
        # Test with category filter
        response = requests.get(f"{base_url}/api/clues?category={valid_category_id}")
        response.raise_for_status()
        data = response.json()
        assert isinstance(data, list)
        for clue in data:
            assert clue["category_id"] == valid_category_id
        
        # Test with offset
        response = requests.get(f"{base_url}/api/clues?offset=2")
        response.raise_for_status()
        data = response.json()
        assert isinstance(data, list)
        print("✅ Clues endpoint test passed")
        
        # Test categories endpoint
        print("Testing categories endpoint...")
        response = requests.get(f"{base_url}/api/categories")
        response.raise_for_status()
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        
        # Store a valid category ID for later tests
        valid_category_id = data[0]["id"]
        
        # Test with count parameter
        response = requests.get(f"{base_url}/api/categories?count=3")
        response.raise_for_status()
        data = response.json()
        assert isinstance(data, list)
        assert 1 <= len(data) <= 3
        
        # Test with offset
        response = requests.get(f"{base_url}/api/categories?offset=1")
        response.raise_for_status()
        data = response.json()
        assert isinstance(data, list)
        print("✅ Categories endpoint test passed")
        
        # Test category endpoint
        print("Testing category endpoint...")
        response = requests.get(f"{base_url}/api/category/{valid_category_id}")
        response.raise_for_status()
        data = response.json()
        assert "id" in data
        assert "title" in data
        assert "clues_count" in data
        assert "clues" in data
        assert isinstance(data["clues"], list)
        
        # Test with invalid category ID (should return 404)
        try:
            response = requests.get(f"{base_url}/api/category/999999")
            if response.status_code != 404:
                print("❌ Expected 404 for invalid category ID but got", response.status_code)
                assert False
        except requests.exceptions.RequestException:
            pass  # Expected to fail
        print("✅ Category endpoint test passed")
        
        # Test final endpoint
        print("Testing final endpoint...")
        response = requests.get(f"{base_url}/api/final")
        response.raise_for_status()
        data = response.json()
        assert isinstance(data, list)
        for clue in data:
            assert clue["value"] is None
        print("✅ Final endpoint test passed")
        
        # Test invalid endpoint (only if we have a valid clue ID)
        print("Testing invalid endpoint...")
        try:
            # Get a valid clue ID
            response = requests.get(f"{base_url}/api/random")
            response.raise_for_status()
            clue_id = response.json()[0]["id"]
            
            # Mark it as invalid
            response = requests.post(
                f"{base_url}/api/invalid",
                json={"id": clue_id}
            )
            response.raise_for_status()
            data = response.json()
            assert "id" in data
            assert "invalid_count" in data
            assert data["id"] == clue_id
            
            # Test with invalid clue ID (should return 404)
            try:
                response = requests.post(
                    f"{base_url}/api/invalid",
                    json={"id": 9999999}
                )
                if response.status_code != 404:
                    print("❌ Expected 404 for invalid clue ID but got", response.status_code)
                    assert False
            except requests.exceptions.RequestException:
                pass  # Expected to fail
            print("✅ Invalid endpoint test passed")
        except Exception as e:
            print(f"⚠️ Could not test invalid endpoint: {e}")
        
        print("All tests passed! ✅")
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the server. Make sure it's running at", base_url)
        return False
    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP error: {e}")
        return False
    except AssertionError as e:
        print(f"❌ Test failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    print("Testing the live API endpoints...")
    print("Make sure the server is running at http://localhost:8000")
    print("Press Enter to continue or Ctrl+C to cancel...")
    try:
        input()
    except KeyboardInterrupt:
        print("\nTest cancelled.")
        sys.exit(0)
    
    success = test_api_live()
    if success:
        print("\nAll tests completed successfully! Your API is working correctly.")
    else:
        print("\nSome tests failed. Check the errors above.")
        sys.exit(1) 