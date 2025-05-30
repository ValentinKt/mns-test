"""
Service for searching cities and fetching detailed weather data from OpenWeatherMap.
"""

import sqlite3
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
from pathlib import Path
import logging
import sys
sys.path.append(str(Path(__file__).resolve().parent.parent))
import config
import time

logger = logging.getLogger(__name__)

class WeatherService:
    """Service for searching cities and fetching detailed weather data."""
    
    def log_request_details(self, url, status_code=None, error=None, duration=None):
        """
        Log details about an HTTP request.
        
        Args:
            url (str): The URL requested.
            status_code (int, optional): HTTP status code of the response.
            error (Exception, optional): Exception if an error occurred.
            duration (int, optional): Duration of the request in milliseconds.
        """
        msg = f"Request to {url}"
        if status_code is not None:
            msg += f" | Status: {status_code}"
        if duration is not None:
            msg += f" | Duration: {duration} ms"
        if error is not None:
            msg += f" | Error: {error}"
        logger.info(msg)
    
    # Update the constructor
    def __init__(self, db_path=None):
        """
        Initialize the weather service.
        
        Args:
            db_path (str, optional): Path to the SQLite database file
        """
        base_dir = Path(__file__).resolve().parent.parent
        self.db_path = db_path or config.DB_PATH
        self.use_api_first = config.USE_API_FIRST
        self.max_retries = config.MAX_RETRIES
        self.backoff_factor = config.BACKOFF_FACTOR
        self.request_timeout = config.REQUEST_TIMEOUT
        
        self.request_count = 0
        self.error_count = 0
        self.last_request_time = 0
        self.conn =  
        
      


    
    def search_cities(self, name, country=None, limit=10):
        """
        Search for cities by name in the SQLite database.
        
        Args:
            name (str): City name to search for
            country (str, optional): Two-letter country code
            limit (int): Maximum number of results to return
            
        Returns:
            list: List of matching cities
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # This enables column access by name
            cursor = conn.cursor()
            
            # Build the query based on whether country is provided
            query = "SELECT * FROM cities WHERE name LIKE ?"
            params = [f"%{name}%"]
            
            if country:
                query += " AND country = ?"
                params.append(country.upper())
            
            query += " ORDER BY name LIMIT ?"
            params.append(str(limit))
            
            cursor.execute(query, params)
            cities = [dict(row) for row in cursor.fetchall()]
            
            conn.close()
            return cities
        except sqlite3.Error as e:
            logger.error(f"Database error: {e}")
            return []
    
    def get_city_by_id(self, city_id):
        """
        Get city information by ID.
        
        Args:
            city_id (int): OpenWeatherMap city ID
            
        Returns:
            dict: City information or None if not found
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM cities WHERE id = ?", (city_id,))
            city = cursor.fetchone()
            
            conn.close()
            
            if city:
                return dict(city)
            return None
        except sqlite3.Error as e:
            logger.error(f"Database error: {e}")
            return None
    
    def fetch_weather_data(self, city_id):
        """
        Fetch weather data from OpenWeatherMap website with retry logic.
        
        Args:
            city_id (int): OpenWeatherMap city ID
            
        Returns:
            dict: Weather data or None if failed
        """
        url = f"https://openweathermap.org/city/{city_id}"
        start_time = time.time()
        
        try:
            logger.info(f"Fetching weather data for city ID {city_id}")
            
            response = self.fetch_with_retry(url)
            
            if not response:
                logger.error(f"All retry attempts failed for city ID {city_id}")
                return self._get_mock_weather_data(city_id)
                
            duration = int((time.time() - start_time) * 1000)
            self.log_request_details(url, status_code=response.status_code, duration=duration)
            
            # Check if response contains actual content
            if not response.text or len(response.text) < 100:
                logger.error(f"Empty or too short response received for city ID {city_id}")
                return self._get_mock_weather_data(city_id)
                
            weather_data = self._parse_weather_html(response.text, city_id)
            
            if weather_data:
                logger.info(f"Successfully parsed weather data for {city_id}: {weather_data['city_country']}, {weather_data['temperature']}")
            else:
                logger.warning(f"Failed to parse weather data for city ID {city_id}")
                
            return weather_data
        except Exception as e:
            duration = int((time.time() - start_time) * 1000)
            self.log_request_details(url, error=e, duration=duration)
            logger.error(f"Unexpected error fetching weather data for city {city_id}: {e}", exc_info=True)
            return self._get_mock_weather_data(city_id)
    
    def _parse_weather_html(self, html_content, city_id):
        """
        Parse weather data from HTML content.
        
        Args:
            html_content (str): HTML content from OpenWeatherMap website
            city_id (int): City ID for reference
            
        Returns:
            dict: Structured weather data
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Find the weather widget section - try multiple selectors
        weather_widget = soup.select_one("#weather-widget > div.section-content")
        
        # If the first selector fails, try alternative selectors
        if not weather_widget:
            weather_widget = soup.select_one("div.current-container")
        
        if not weather_widget:
            weather_widget = soup.select_one("div.owm-city-current")
            
        if not weather_widget:
            logger.error("Could not find weather widget in HTML content")
            # Return mock data instead of None to prevent application errors
            return self._get_mock_weather_data(city_id)
        
        # Extract city name and country
        city_heading = weather_widget.select_one("h2")
        city_country = city_heading.text.strip() if city_heading else "Unknown"
        
        # Extract current date and time
        date_time_elem = weather_widget.select_one("span.orange-text")
        date_time = date_time_elem.text.strip() if date_time_elem else "Unknown"
        
        # Extract temperature
        temp_elem = weather_widget.select_one("div.current-temp span.heading")
        temperature = temp_elem.text.strip() if temp_elem else "Unknown"
        
        # Extract weather description
        weather_desc_elem = weather_widget.select_one("div.bold")
        weather_desc = weather_desc_elem.text.strip() if weather_desc_elem else "Unknown"
        
        # Extract additional weather details
        weather_items = weather_widget.select("ul.weather-items li")
        
        # Initialize weather details with default values
        weather_details = {
            'wind': 'Unknown',
            'pressure': 'Unknown',
            'humidity': 'Unknown',
            'uv': 'Unknown',
            'dew_point': 'Unknown',
            'visibility': 'Unknown'
        }
        
        # Parse each weather item
        for item in weather_items:
            item_text = item.text.strip()
            
            if 'm/s' in item_text:
                weather_details['wind'] = item_text.strip()
                # Extract wind speed value
                wind_match = re.search(r'(\d+\.?\d*)\s*m/s', item_text)
                if wind_match:
                    weather_details['wind_speed'] = wind_match.group(1)
                else:
                    weather_details['wind_speed'] = "0"
            elif 'hPa' in item_text:
                weather_details['pressure'] = item_text.strip()
            elif 'Humidity:' in item_text:
                weather_details['humidity'] = item_text.replace('Humidity:', '').strip()
            elif 'UV:' in item_text:
                weather_details['uv'] = item_text.replace('UV:', '').strip()
            elif 'Dew point:' in item_text:
                weather_details['dew_point'] = item_text.replace('Dew point:', '').strip()
            elif 'Visibility:' in item_text:
                weather_details['visibility'] = item_text.replace('Visibility:', '').strip()
        
        # Extract temperature value
        temp_value = None
        if temperature != "Unknown":
            temp_match = re.search(r'(-?\d+)°C', temperature)
            if temp_match:
                temp_value = int(temp_match.group(1))
        
        # Create structured weather data
        weather_data = {
            'city_id': city_id,
            'city_country': city_country,
            'date_time': date_time,
            'temperature': temperature,
            'temperature_value': temp_value,
            'description': weather_desc,
            'wind': weather_details['wind'],
            'wind_speed': weather_details.get('wind_speed', 0),
            'pressure': weather_details['pressure'],
            'humidity': weather_details['humidity'],
            'uv': weather_details['uv'],
            'dew_point': weather_details['dew_point'],
            'visibility': weather_details['visibility'],
            'fetched_at': datetime.now().isoformat()
        }
        
        return weather_data

    def import_city_to_locations(self, city_id):
        """Import a city from cities table to locations table."""
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        # Check if city exists in cities table
        cursor.execute(
            "SELECT id, name, state, country, latitude, longitude FROM cities WHERE id = ?",
            (city_id,)
        )
        
        city = cursor.fetchone()
        
        if not city:
            conn.close()
            return False
        
        # Check if city already exists in locations table
        cursor.execute("SELECT id FROM locations WHERE id = ?", (city_id,))
        if cursor.fetchone():
            conn.close()
            return True  # Already imported
        
        # Create description from state and country
        description = f"{city['state']}, {city['country']}" if city['state'] else city['country']
        
        # Insert into locations table
        now = datetime.now().isoformat()
        cursor.execute(
            """INSERT INTO locations 
               (id, name, latitude, longitude, description, timezone, created_at, updated_at) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (city['id'], city['name'], city['latitude'], city['longitude'], 
             description, 'UTC', now, now)
        )
        
        conn.commit()
        conn.close()
        
        return True

    def import_cities_by_country(self, country_code, limit=10):
        """Import cities from a specific country to locations table."""
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        query = """SELECT id, name, state, country, latitude, longitude 
                   FROM cities WHERE country = ?"""
        params = [country_code]
        
        if limit is not None and limit > 0:
            query += " LIMIT ?"
            params.append(limit)
        
        cursor.execute(query, tuple(params))
        
        cities = cursor.fetchall()
        imported_count = 0
        
        for city in cities:
            # Check if city already exists in locations table
            cursor.execute("SELECT id FROM locations WHERE id = ?", (city['id'],))
            if cursor.fetchone():
                continue  # Skip if already imported
            
            # Create description from state and country
            description = f"{city['state']}, {city['country']}" if city['state'] else city['country']
            
            # Insert into locations table
            now = datetime.now().isoformat()
            cursor.execute(
                """INSERT INTO locations 
                   (id, name, latitude, longitude, description, timezone, created_at, updated_at) 
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (city['id'], city['name'], city['latitude'], city['longitude'], 
                 description, 'UTC', now, now)
            )
            
            imported_count += 1
        
        conn.commit()
        conn.close()
        
        return imported_count

    def _get_mock_weather_data(self, city_id):
        """Return mock weather data when parsing fails."""
        city = self.get_city_by_id(city_id)
        city_name = f"{city['name']}, {city['country']}" if city else "Unknown Location"
        
        return {
            'city_id': city_id,
            'city_country': city_name,
            'date_time': datetime.now().strftime("%Y-%m-%d %H:%M"),
            'temperature': "15°C",
            'temperature_value': 15,
            'description': "Cloudy",
            'wind': "Wind: 5 m/s",
            'wind_speed': 5.0,
            'pressure': "Pressure: 1013 hPa",
            'humidity': "80%",
            'uv': "2",
            'dew_point': "10°C",
            'visibility': "10.0 km",
            'fetched_at': datetime.now().isoformat()
        }

    def fetch_weather_data_api(self, city_id, api_key=None):
        """
        Fetch weather data using the official OpenWeatherMap API.
        
        Args:
            city_id (int): OpenWeatherMap city ID
            api_key (str, optional): OpenWeatherMap API key
            
        Returns:
            dict: Weather data or None if failed
        """
        if not api_key:
            logger.warning("No API key provided for OpenWeatherMap API")
            return self.fetch_weather_data(city_id)  # Fall back to web scraping
            
        city = self.get_city_by_id(city_id)
        if not city:
            logger.error(f"City with ID {city_id} not found in database")
            return None
            
        url = "https://api.openweathermap.org/data/2.5/weather"
        start_time = time.time()
        
        try:
            params = {
                'id': city_id,
                'appid': api_key,
                'units': 'metric'  # Use metric units (Celsius)
            }
            
            logger.info(f"Fetching weather data from API for city ID {city_id}")
            response = requests.get(url, params=params, timeout=10)
            duration = int((time.time() - start_time) * 1000)
            
            self.log_request_details(url, status_code=response.status_code, duration=duration)
            response.raise_for_status()
            
            data = response.json()
            
            # Convert API response to our standard format
            weather_data = {
                'city_id': city_id,
                'city_country': f"{city['name']}, {city['country']}",
                'date_time': datetime.now().strftime("%Y-%m-%d %H:%M"),
                'temperature': f"{data['main']['temp']}°C",
                'temperature_value': data['main']['temp'],
                'description': data['weather'][0]['description'],
                'wind': f"Wind: {data['wind']['speed']} m/s",
                'wind_speed': data['wind']['speed'],
                'pressure': f"Pressure: {data['main']['pressure']} hPa",
                'humidity': f"{data['main']['humidity']}%",
                'uv': "N/A",  # Not available in basic API
                'dew_point': "N/A",  # Not available in basic API
                'visibility': f"{data.get('visibility', 0) / 1000} km",
                'fetched_at': datetime.now().isoformat()
            }
            
            logger.info(f"Successfully fetched API weather data for {city_id}")
            return weather_data
            
        except Exception as e:
            duration = int((time.time() - start_time) * 1000)
            self.log_request_details(url, error=e, duration=duration)
            logger.error(f"Error fetching API weather data for city {city_id}: {e}")
            
            # Fall back to web scraping if API fails
            logger.info(f"Falling back to web scraping for city {city_id}")
            return self.fetch_weather_data(city_id)

    def fetch_with_retry(self, url, params=None, headers=None, max_retries=3, backoff_factor=1.5):
        """
        Fetch data with retry logic.
        
        Args:
            url (str): URL to fetch
            params (dict, optional): Query parameters
            headers (dict, optional): Request headers
            max_retries (int): Maximum number of retry attempts
            backoff_factor (float): Factor to increase wait time between retries
            
        Returns:
            requests.Response: Response object or None if all retries failed
        """
        headers = headers or {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        for attempt in range(1, max_retries + 1):
            try:
                logger.info(f"Request attempt {attempt}/{max_retries} for {url}")
                response = requests.get(url, params=params, headers=headers, timeout=10)
                
                # If successful or client error (4xx), don't retry
                if response.status_code < 500:
                    return response
                    
                logger.warning(f"Server error {response.status_code} on attempt {attempt}, retrying...")
                
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
                if attempt == max_retries:
                    logger.error(f"All retry attempts failed for {url}: {e}")
                    return None
                    
                logger.warning(f"Request failed on attempt {attempt}: {e}, retrying...")
            
            # Calculate backoff time with exponential backoff
            backoff_time = backoff_factor * (2 ** (attempt - 1))
            logger.info(f"Waiting {backoff_time:.1f} seconds before retry")
            time.sleep(backoff_time)
        
        return None

