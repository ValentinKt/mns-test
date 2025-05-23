#!/usr/bin/env python3
"""
Script to create additional tables in the cities.db database.
This adds the locations, weather_data, and tidal_data tables.
"""

import sqlite3
import os
from pathlib import Path

# Define paths
BASE_DIR = Path(__file__).resolve().parent.parent
DB_FILE = BASE_DIR / 'data' / 'cities.db'

def create_tables():
    """Create additional tables in the SQLite database."""
    print(f"Adding tables to database at {DB_FILE}...")
    
    # Check if database file exists
    if not DB_FILE.exists():
        print(f"Error: Database file not found at {DB_FILE}")
        print("Please run json_to_sqlite.py first to create the database.")
        return
    
    # Connect to database
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Create locations table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS locations (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        latitude REAL NOT NULL,
        longitude REAL NOT NULL,
        description TEXT,
        timezone TEXT DEFAULT 'UTC',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Create weather_data table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS weather_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        location_id INTEGER NOT NULL,
        date TEXT NOT NULL,
        temperature REAL NOT NULL,
        condition TEXT NOT NULL,
        wind_speed REAL,
        sunrise TEXT,
        sunset TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (location_id) REFERENCES locations (id) ON DELETE CASCADE
    )
    ''')
    
    # Create tidal_data table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tidal_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        location_id INTEGER NOT NULL,
        date TEXT NOT NULL,
        coefficient REAL,
        high_tide_time TEXT,
        low_tide_time TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (location_id) REFERENCES locations (id) ON DELETE CASCADE
    )
    ''')
    
    # Create indexes for faster queries
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_location_name ON locations (name)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_weather_location_date ON weather_data (location_id, date)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_tidal_location_date ON tidal_data (location_id, date)')
    
    # Add some sample locations from the cities table
    cursor.execute('''
    INSERT OR IGNORE INTO locations (id, name, latitude, longitude, description, timezone)
    SELECT id, name, latitude, longitude, country, 'UTC'
    FROM cities
    WHERE country = 'FR'
    LIMIT 10
    ''')
    
    # Commit changes and close connection
    conn.commit()
    conn.close()
    
    print("Tables created successfully!")
    print("Added sample locations from cities table.")

if __name__ == "__main__":
    create_tables()