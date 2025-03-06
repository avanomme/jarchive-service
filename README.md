# jService API

A JSON API serving Jeopardy trivia questions. This is a simplified version that serves pre-processed data from a JSON file for maximum performance.

## Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Generate the JSON data (optional, only if you want to rebuild from source):

```bash
python transform_data.py
```

3. Run the API server:

```bash
python api.py
```

## API Endpoints

- `/api/category/{id}` - Get a specific category and all its clues
- `/api/random` - Get a random category with its clues
- `/api/categories` - Get all categories

## Data Format

Categories are returned in this format:

```json
{
  "id": 1,
  "title": "Category Title",
  "created_at": "2024-03-06T00:00:00.000Z",
  "updated_at": "2024-03-06T00:00:00.000Z",
  "clues_count": 25,
  "clues": [
    {
      "id": 1,
      "answer": "Answer text",
      "question": "Question text",
      "value": 200,
      "airdate": "1984-09-10T00:00:00.000Z",
      "category_id": 1,
      "game_id": 1,
      "invalid_count": null
    },
    ...
  ]
}
```

## Deployment

The API is deployed on Render.com. The deployment configuration is in `render.yaml`.

## Data Source

The data comes from `combined_season1-40.tsv`, which contains Jeopardy! questions from seasons 1-40.
