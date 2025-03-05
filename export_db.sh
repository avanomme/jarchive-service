#!/bin/bash

# Export the database to a SQL file
echo "Exporting jservice database to jservice_dump.sql..."
pg_dump -c -U Adam jservice > jservice_dump.sql

echo "Export completed. File size:"
du -sh jservice_dump.sql

echo "To import this database into Render.com:"
echo "1. Go to the Render.com dashboard"
echo "2. Create a new PostgreSQL database"
echo "3. Connect to the database using the provided connection string"
echo "4. Import the SQL file using: psql <connection_string> < jservice_dump.sql" 