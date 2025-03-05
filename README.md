# jService API

A Ruby on Rails API service that provides access to Jeopardy! game data. This project is part of CS3130 coursework.

## Features

- RESTful API endpoints for Jeopardy! clues and categories
- API key authentication
- PostgreSQL database with full-text search capabilities
- Docker support for easy deployment

## Prerequisites

- Ruby 3.4.1
- PostgreSQL
- Docker (optional)

## Setup

1. Clone the repository:

```bash
git clone https://github.com/avanomme/3130-jservice.git
cd 3130-jservice
```

2. Install dependencies:

```bash
bundle install
```

3. Set up the database:

```bash
bundle exec rails db:create db:migrate
```

4. Generate an API key:

```bash
bundle exec rake "api_keys:generate[Your Key Name]"
```

5. Start the server:

```bash
bundle exec rails server
```

## Docker Setup

1. Build and start the containers:

```bash
docker-compose up --build
```

## API Documentation

The API requires authentication using an API key. Include your API key in the request header:

```
Authorization: Bearer your-api-key-here
```

### Available Endpoints

- `GET /api/v1/categories` - List all categories
- `GET /api/v1/categories/:id` - Get a specific category
- `GET /api/v1/clues` - List all clues
- `GET /api/v1/clues/:id` - Get a specific clue
- `GET /api/v1/random` - Get a random clue

## License

This project is private and intended for CS3130 coursework only.
