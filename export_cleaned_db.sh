#!/bin/bash

echo "Exporting jService database with cleaned category names to jservice_cleaned.sql..."
pg_dump -U Adam jservice > jservice_cleaned.sql

echo "Export complete. The file jservice_cleaned.sql has been created."
echo "To import this database into Render.com:"
echo "1. Go to the Render.com dashboard"
echo "2. Create a new PostgreSQL database"
echo "3. Connect to the database using the provided connection string"
echo "4. Import the SQL file using: psql <connection_string> < jservice_cleaned.sql" 