#!/usr/bin/env python3
"""
Script to convert city.list.min.json to a SQLite database.
This creates a cities table with all the city information.
"""

import json
import sqlite3
import os
import sys
from pathlib import Path

# Define paths
BASE_DIR = Path(__file__).resolve().parent.parent
JSON_FILE = BASE_DIR / 'data' / 'city.list.min.json'
DB_FILE = BASE_DIR / 'data' / 'cities.db'

def create_database():
    """Create SQLite database from JSON file."""
    print(f"Converting {JSON_FILE} to SQLite database...")
    
    # Check if JSON file exists
    if not JSON_FILE.exists():
        print(f"Error: JSON file not found at {JSON_FILE}")
        sys.exit(1)
    
    # Create data directory if it doesn't exist
    os.makedirs(BASE_DIR / 'data', exist_ok=True)
    
    # Remove existing database if it exists
    if DB_FILE.exists():
        os.remove(DB_FILE)
    
    # Connect to database
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Create cities table
    cursor.execute('''
    CREATE TABLE cities (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        state TEXT,
        country TEXT NOT NULL,
        latitude REAL NOT NULL,
        longitude REAL NOT NULL
    )
    ''')
    
    # Create index on name and country for faster searches
    cursor.execute('CREATE INDEX idx_city_name ON cities (name)')
    cursor.execute('CREATE INDEX idx_city_country ON cities (country)')
    
    # Load JSON data
    try:
        with open(JSON_FILE, 'r', encoding='utf-8') as f:
            cities = json.load(f)
    except json.JSONDecodeError:
        print("Error: Invalid JSON format in the input file")
        conn.close()
        sys.exit(1)
    
    # Insert data into database
    count = 0
    for city in cities:
        try:
            cursor.execute(
                'INSERT INTO cities VALUES (?, ?, ?, ?, ?, ?)',
                (
                    city['id'],
                    city['name'],
                    city['state'],
                    city['country'],
                    city['coord']['lat'],
                    city['coord']['lon']
                )
            )
            count += 1
            if count % 1000 == 0:
                print(f"Processed {count} cities...")
        except KeyError as e:
            print(f"Warning: Missing key {e} in city data, skipping record")
        except sqlite3.Error as e:
            print(f"Error inserting city {city.get('name', 'unknown')}: {e}")
    
    # Commit changes and close connection
    conn.commit()
    conn.close()
    
    print(f"Conversion complete! {count} cities added to database.")
    print(f"Database saved to {DB_FILE}")

if __name__ == "__main__":
    create_database()