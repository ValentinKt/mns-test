import sqlite3
import os
from pathlib import Path

class Connection:

     # Create a connection to the SQLite database using the singleton pattern
    _db_connection = None

    def __init__(self, db_name='cities.db'):
        """Initialize the Connection class with a database name."""
        self.db_name = db_name
        self.connected = False

    @staticmethod
    def get_db_connection():
        """Get a singleton connection to the SQLite database."""
        global _db_connection
        if _db_connection is None:
            app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            db_path = os.path.join(app_dir, 'data', 'cities.db')
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
            _db_connection = sqlite3.connect(db_path)
            _db_connection.row_factory = sqlite3.Row
        return _db_connection

    @staticmethod
    def close_db_connection():
        """Close the singleton connection to the SQLite database."""
        global _db_connection
        if _db_connection is not None:
            _db_connection.close()
            _db_connection = None

    def connect(self):
        if not self.connected:
            print(f"Connecting to database: {self.db_name}")
            self.connected = True
        else:
            print("Already connected.")

    def disconnect(self):
        if self.connected:
            print(f"Disconnecting from database: {self.db_name}")
            self.connected = False
        else:
            print("Already disconnected.")
    def execute_query(self, query):
        if not self.connected:
            raise Exception("Not connected to the database.")
        print(f"Executing query: {query}")
        # Here you would normally execute the query against the database
        # For this example, we'll just simulate it
        
        return f"Results for query: {query}"
    def fetch_results(self, query):
        if not self.connected:
            raise Exception("Not connected to the database.")
        print(f"Fetching results for query: {query}")
        # Simulate fetching results
        return f"Fetched results for query: {query}"
    def close(self):
        if self.connected:
            print(f"Closing connection to database: {self.db_name}")
            self.connected = False
        else:
            print("Connection already closed.")
        # Check if the request was successful
        return True
