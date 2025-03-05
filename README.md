# jService API

A simple FastAPI application that serves Jeopardy! clues and categories.

## Deployment to Render.com

### Prerequisites

- A Render.com account
- The PostgreSQL dump file (jservice_cleaned.sql)

### Steps to Deploy

1. Push this repository to GitHub or another Git provider.

2. Log in to Render.com and click on the "New +" button.

3. Select "Blueprint" and provide the URL to your Git repository.

4. Render will automatically detect the `render.yaml` file and set up both:

   - A PostgreSQL database (jservice-db)
   - A web service (jservice-api)

5. After the initial deployment, you'll need to import the database:
   - Go to your PostgreSQL database in the Render dashboard
   - Copy the External Connection String
   - Use the following command to import your data:
     ```
     psql <connection_string> < jservice_cleaned.sql
     ```

## API Endpoints

- `/api/random?count=1` - Get random clues
- `/api/categories?count=10&offset=0` - Get categories with pagination
- `/api/category/{id}` - Get a specific category and its clues
- `/api/clues?value=200&category=1` - Get clues with optional filters
- `/api/final?count=1` - Get random Final Jeopardy! clues
- `/api/invalid` - Mark a clue as invalid (POST with JSON: `{"id": 1}`)

## Local Development

1. Create a virtual environment:

   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:

   ```
   pip install -r requirements.txt
   ```

3. Set up a local PostgreSQL database named "jservice".

4. Import the database:

   ```
   psql -U username jservice < jservice_cleaned.sql
   ```

5. Run the application:

   ```
   uvicorn app:app --reload
   ```

6. Visit http://localhost:8000 in your browser.

## Notes

- The categories have been cleaned from the original database to remove Alex Trebek's commentary.
- For categories where the actual title couldn't be clearly determined, the title was set to "UNKNOWN".
