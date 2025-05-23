#!/usr/bin/env python3
"""
Script to load data into locations, tidal_data, and weather_data tables.
This script imports cities from cities.db and fetches tidal and weather data for each location.
"""

import os
import sys
from datetime import date
import logging

# Add parent directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import Location, TidalData, WeatherData
from services.weather_service import WeatherService
from services.tidal_api import TidalAPIService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def import_locations(weather_service, country_code='FR', limit=1000):
    """
    Import locations from cities table to locations table.
    
    Args:
        weather_service (WeatherService): Instance of WeatherService
        country_code (str): Country code to filter cities
        limit (int): Maximum number of cities to import
        
    Returns:
        list: List of imported Location objects
    """
    logger.info(f"Importing up to {limit} locations from country {country_code}")
    
    # Import cities from the specified country
    imported_count = weather_service.import_cities_by_country(country_code, limit)
    logger.info(f"Imported {imported_count} new locations")
    
    # Get all locations
    locations = Location.get_all()
    logger.info(f"Total locations in database: {len(locations)}")
    
    return locations

def fetch_tidal_data(tidal_service, locations):
    """
    Fetch and store tidal data for each location.
    
    Args:
        tidal_service (TidalAPIService): Instance of TidalAPIService
        locations (list): List of Location objects
        
    Returns:
        int: Number of locations with tidal data fetched
    """
    logger.info(f"Fetching tidal data for {len(locations)} locations")
    today = date.today()
    count = 0
    
    for location in locations:
        # Check if tidal data already exists for this location and date
        existing_data = TidalData.get_by_location_and_date(location.id, today)
        if existing_data:
            logger.info(f"Tidal data already exists for location {location.name} on {today}")
            count += 1
            continue
        
        # Fetch tidal data
        logger.info(f"Fetching tidal data for {location.name} ({location.id})")
        tidal_data_dict = tidal_service.get_tidal_data(
            location.latitude, 
            location.longitude, 
            location.id
        )
        
        if tidal_data_dict:
            # Save to database
            tidal_data = TidalData(
                location_id=location.id,
                date=today,
                coefficient=tidal_data_dict.get('coefficient', 0),
                high_tide_time=tidal_data_dict.get('high_tide_time', 'N/A'),
                low_tide_time=tidal_data_dict.get('low_tide_time', 'N/A')
            )
            tidal_data.save()
            logger.info(f"Saved tidal data for {location.name}")
            count += 1
        else:
            logger.error(f"Failed to fetch tidal data for {location.name}")
    
    return count

def fetch_weather_data(weather_service, locations):
    """
    Fetch and store weather data for each location.
    
    Args:
        weather_service (WeatherService): Instance of WeatherService
        locations (list): List of Location objects
        
    Returns:
        int: Number of locations with weather data fetched
    """
    logger.info(f"Fetching weather data for {len(locations)} locations")
    today = date.today()
    count = 0
    
    for location in locations:
        # Check if weather data already exists for this location and date
        existing_data = WeatherData.get_by_location_and_date(location.id, today)
        if existing_data:
            logger.info(f"Weather data already exists for location {location.name} on {today}")
            count += 1
            continue
        
        # Fetch weather data
        logger.info(f"Fetching weather data for {location.name} ({location.id})")
        weather_data_dict = weather_service.fetch_weather_data(location.id)
        
        if weather_data_dict:
            # Save to database
            weather_data = WeatherData(
                location_id=location.id,
                date=today,
                temperature=weather_data_dict.get('temperature_value', 0),
                condition=weather_data_dict.get('description', 'Unknown'),
                wind_speed=weather_data_dict.get('wind_speed', 0),
                sunrise=weather_data_dict.get('sunrise', ''),
                sunset=weather_data_dict.get('sunset', '')
            )
            weather_data.save()
            logger.info(f"Saved weather data for {location.name}")
            count += 1
        else:
            logger.error(f"Failed to fetch weather data for {location.name}")
    
    return count

def main():
    """Main function to load data into tables."""
    logger.info("Starting data loading process")
    
    # Initialize services
    weather_service = WeatherService()
    tidal_service = TidalAPIService()
    
    # Import locations - Set limit to None to import all locations for the country_code
    locations = import_locations(weather_service, country_code='FR', limit=None)
    
    if not locations:
        logger.error("No locations found or imported. Exiting.")
        return
    
    # Fetch and store tidal data
    tidal_count = fetch_tidal_data(tidal_service, locations)
    logger.info(f"Tidal data fetched for {tidal_count}/{len(locations)} locations")
    
    # Fetch and store weather data
    weather_count = fetch_weather_data(weather_service, locations)
    logger.info(f"Weather data fetched for {weather_count}/{len(locations)} locations")
    
    logger.info("Data loading process completed")

if __name__ == "__main__":
    main()