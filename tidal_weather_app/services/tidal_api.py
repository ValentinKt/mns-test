import os
import requests
import logging
from datetime import date, datetime, timedelta
from services.cache import get_cached_data, cache_data
from services.tidal_scraper import TidalScraperService
import requests
import math
from datetime import datetime

logger = logging.getLogger(__name__)

class TidalAPIService:
    """Service for fetching tidal data from WorldTides API."""
    

    def __init__(self):  
        logger.info("Initializing TidalAPIService with web scraping")
        self.scraper = TidalScraperService()

    def get_tidal_data(self, latitude, longitude, location_id, city_name=None):
        """
        Fetch tidal data for a specific location.
        
        Args:©
            latitude (float): Location latitude
            longitude (float): Location longitude
            location_id (int): Location ID for caching
            city_name (str, optional): City name for scraping
            
        Returns:
            dict: Tidal data
        """
        cache_key = f"tidal_{location_id}_{date.today().isoformat()}"
        cached_data = get_cached_data(cache_key)
        
        if cached_data:
            logger.info(f"Using cached tidal data for location {location_id}")
            return cached_data
        
        # If city_name is provided, try to scrape data
        if city_name:
            logger.info(f"Attempting to scrape tidal data for {city_name}")
            scraped_data = self.scraper.get_tidal_data_by_city(city_name, location_id)
            if scraped_data:
                return scraped_data
        
        # Fall back to mock data if scraping fails or city_name not provided
        logger.warning(f"Could not scrape tidal data for location {location_id}, using mock data")
        return self.get_mock_tidal_data()

    def get_mock_tidal_data(self):
        """
        Returns mock tidal data.
        """
        # Mock tidal data for demonstration purposes
        logger.info("Returning mock tidal data")
        tidal_data = {
            "location_id": 1,
            "date": date.today().isoformat(),
            "high_tides": [
                {"time": "06:00", "height": 2.5},
                {"time": "18:00", "height": 2.7}
            ],
            "low_tides": [
                {"time": "12:00", "height": 0.5},
                {"time": "00:00", "height": 0.3}
            ],
            "tidal_coefficient": 80
        }
        cache_data(f"tidal_{tidal_data['location_id']}_{date.today().isoformat()}", tidal_data)
        return tidal_data

    def calculate_tidal_coefficient(self, sun_distance, moon_distance):
        """
        Calculate the tidal coefficient based on the distances of the Sun and Moon from Earth.
        
        :param sun_distance: Distance from Earth to the Sun in kilometers
        :param moon_distance: Distance from Earth to the Moon in kilometers
        :return: Tidal coefficient
        """
        # Constants
        sun_radius = 696340  # Radius of the Sun in kilometers
        moon_radius = 1737  # Radius of the Moon in kilometers
        earth_radius = 6371  # Radius of the Earth in kilometers
        
        # Tidal forces
        sun_tidal_force = (sun_radius / sun_distance) ** 3
        moon_tidal_force = (moon_radius / moon_distance) ** 3
        
        # Tidal coefficient
        tidal_coefficient = (sun_tidal_force + moon_tidal_force) * 100
        
        return min(tidal_coefficient, 120)

        # Example usage
        sun_distance = 149.6e6  # Average distance from Earth to the Sun in kilometers
        moon_distance = 384400  # Average distance from Earth to the Moon in kilometers

        tidal_coefficient = calculate_tidal_coefficient(sun_distance, moon_distance)
        print(f"Tidal Coefficient: {tidal_coefficient}")

    def fetch_marine_weather_data(self, latitude, longitude):
        """
        Fetch marine weather data from the Open-Meteo API.
        
        :param latitude: Latitude of the location
        :param longitude: Longitude of the location
        :return: Weather data as a dictionary
        """
        url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&hourly=temperature_2m,relativehumidity_2m,wind_speed_10m,wind_direction_10m,pressure_msl,precipitation,cloudcover,wave_height,wave_direction"
        
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            return None

        # Example usage
        latitude = 48.8566  # Paris, France
        longitude = 2.3522  # Paris, France

        weather_data = fetch_marine_weather_data(latitude, longitude)
        if weather_data:
            return weather_data
        else:
            print("Failed to fetch weather data.")
