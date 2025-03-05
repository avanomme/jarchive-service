# jService API

A JSON API for Jeopardy trivia questions, based on the original jService created by [Steve Ottenad](https://github.com/sottenad).

## Deployment to Render.com

### Prerequisites

- A Render.com account
- The PostgreSQL dump file (`jservice_cleaned.sql`)
- Git installed on your computer

### Steps

1. Push this repository to GitHub (or any Git provider that Render supports)

2. Log into Render.com and select "Blueprint" from the dashboard

3. Connect your GitHub repository and follow the prompts to deploy the blueprint

4. After deployment is complete, connect to the PostgreSQL database:
   ```
   PGPASSWORD=your_password psql -h your-db-host.render.com -U your_username your_database < jservice_cleaned.sql
   ```

### Database Initialization

If you're experiencing a "Database not initialized" error in the API, you have two options:

1. **Import the full jService database:**

   Connect to your Render PostgreSQL database and import the database dump:

   ```bash
   PGPASSWORD=your_password psql -h your-db-host.render.com -U your_username your_database < jservice_cleaned.sql
   ```

2. **Use sample data for testing:**

   Run the setup script to create tables and populate sample data:

   ```bash
   python setup_db.py
   ```

### Troubleshooting

If you encounter a 500 Internal Server Error with "relation does not exist" in the logs:

1. Make sure you've imported the database
2. Check the database connection string in your environment variables
3. Run the setup script to create tables with sample data

## API Endpoints

The API provides the following endpoints:

- `GET /api/random` - Get a random clue
- `GET /api/clues` - Get clues with optional filters
- `GET /api/categories` - Get categories with pagination
- `GET /api/category?id={id}` - Get a specific category by ID (query parameter format for Flutter app)
- `GET /api/category/{id}` - Get a specific category by ID
- `GET /api/final` - Get random final jeopardy clues
- `POST /api/invalid` - Mark a clue as invalid

## Local Development

### Setup

1. Create a virtual environment:

   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install the dependencies:

   ```
   pip install -r requirements.txt
   ```

3. Create a PostgreSQL database:

   ```
   createdb jservice
   ```

4. Import the database (optional - or use setup_db.py for sample data):

   ```
   psql jservice < jservice_cleaned.sql
   ```

5. Initialize the database with sample data if needed:

   ```
   python setup_db.py
   ```

6. Run the application:
   ```
   uvicorn app:app --reload
   ```

The API will be available at http://localhost:8000

## Notes

- The categories have been cleaned from the original database to remove Alex Trebek's commentary.
- For categories where the actual title couldn't be clearly determined, the title was set to "UNKNOWN".
