import sqlite3
import os
from pathlib import Path

def get_db_connection():
    """Get a connection to the SQLite database."""
    app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(app_dir, 'data', 'cities.db')
    
    # Ensure the directory exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

# Import models after defining connection function
from models.location import Location
from models.weather_data import WeatherData
from models.tidal_data import TidalData