# jService API (Python Version)

A lightweight Python implementation of the jService API using FastAPI.

## Local Setup

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Set up your PostgreSQL database and import the jService data
4. Run the API:
   ```
   uvicorn app:app --reload
   ```

## Environment Variables

- `DATABASE_URL`: PostgreSQL connection string
- `PORT`: Port to run the server on (default: 8000)

## API Endpoints

- `/api/random?count=1` - Get random clues
- `/api/clues?value=200&category=11&min_date=...&max_date=...&offset=0` - Get clues with filters
- `/api/categories?count=5&offset=0` - Get categories with pagination
- `/api/category/123` - Get a specific category with its clues
- `/api/final?count=1` - Get random final jeopardy clues
- `/api/invalid` - Mark a clue as invalid (POST request with `{"id": 123}`)

## Deployment

This application can be easily deployed to various platforms:

### Render

1. Create a new Web Service
2. Connect your GitHub repository
3. Set the build command: `pip install -r requirements.txt`
4. Set the start command: `uvicorn app:app --host 0.0.0.0 --port $PORT`
5. Add environment variables (DATABASE_URL)

### Railway

1. Create a new project
2. Connect your GitHub repository
3. Add environment variables (DATABASE_URL)
4. Railway will detect the Procfile and automatically deploy

### Heroku

1. Create a new app
2. Connect your GitHub repository
3. Add the PostgreSQL add-on
4. Deploy
