"""
Configuration settings for the Tidal Weather App.
"""

import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent

# Database settings
DB_PATH = BASE_DIR / 'data' / 'cities.db'

# API settings
USE_API_FIRST = False

# Request settings
MAX_RETRIES = 3
BACKOFF_FACTOR = 1.5
REQUEST_TIMEOUT = 10

# Logging settings
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
LOG_FILE = BASE_DIR / 'logs' / 'app.log'

# Ensure log directory exists
os.makedirs(BASE_DIR / 'logs', exist_ok=True)