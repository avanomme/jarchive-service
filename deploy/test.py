#!/usr/bin/env python3

import sqlite3

# Connect to SQLite database
conn = sqlite3.connect('../jarchive/db.db')
cursor = conn.cursor()

# Count categories
cursor.execute("SELECT COUNT(*) FROM categories")
category_count = cursor.fetchone()[0]

print(f"Database contains {category_count} categories")

# Close the connection
conn.close()
