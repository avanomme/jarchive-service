#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}jService API Test Suite${NC}"
echo "--------------------"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is not installed. Please install Python 3 and try again.${NC}"
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo -e "${RED}Error: pip3 is not installed. Please install pip3 and try again.${NC}"
    exit 1
fi

# Install dependencies
echo -e "Installing dependencies..."
pip3 install -r requirements.txt > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Failed to install dependencies.${NC}"
    exit 1
fi
echo -e "${GREEN}Dependencies installed successfully.${NC}"

# Run mock tests
echo -e "\nRunning mock API tests..."
python3 mock_test.py
if [ $? -ne 0 ]; then
    echo -e "${RED}Mock tests failed. See errors above.${NC}"
    exit 1
fi

# Ask if user wants to run the server for live tests
echo -e "\n${YELLOW}Do you want to start the API server and run live tests? (y/n)${NC}"
read -r answer
if [[ "$answer" =~ ^[Yy]$ ]]; then
    # Start the server in the background
    echo -e "Starting the API server..."
    python3 -m uvicorn app:app --reload > server.log 2>&1 &
    SERVER_PID=$!
    
    # Wait for the server to start
    echo -e "Waiting for the server to start..."
    sleep 3
    
    # Run live tests
    echo -e "\nRunning live API tests..."
    python3 live_test.py
    TEST_RESULT=$?
    
    # Kill the server
    echo -e "Stopping the API server..."
    kill $SERVER_PID > /dev/null 2>&1
    
    if [ $TEST_RESULT -ne 0 ]; then
        echo -e "${RED}Live tests failed. See errors above.${NC}"
        exit 1
    fi
else
    echo -e "Skipping live tests."
fi

echo -e "\n${GREEN}All tests completed successfully!${NC}"
echo -e "Your jService API is working correctly." 