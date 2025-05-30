#!/usr/bin/env python3
"""
Service for scraping tidal data from WorldTides.info website.
This provides an alternative to the API when an API key is not available.
"""

import requests
from bs4 import BeautifulSoup
import logging
from datetime import datetime
import re
from services.cache import get_cached_data, cache_data

logger = logging.getLogger(__name__)

class TidalScraperService:
    """Service for scraping tidal data from WorldTides.info website."""
    
    BASE_URL = "https://www.worldtides.info/tidestations/Europe/France"
    
    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'
        }
    
    def format_city_name(self, city_name):
        """
        Format city name for URL.
        
        Args:
            city_name (str): City name
            
        Returns:
            str: Formatted city name for URL
        """
        # Replace spaces with underscores and handle special characters
        formatted = city_name.replace(' ', '_').replace('-', '_').replace("'", '_')
        return formatted
    
    def get_tidal_data_by_city(self, city_name, location_id):
        """
        Fetch tidal data for a specific city by scraping the website.
        
        Args:
            city_name (str): City name
            location_id (int): Location ID for caching
            
        Returns:
            dict: Tidal data
        """
        cache_key = f"tidal_scrape_{location_id}_{datetime.now().strftime('%Y-%m-%d')}"
        cached_data = get_cached_data(cache_key)
        
        if cached_data:
            logger.info(f"Using cached tidal data for location {location_id}")
            return cached_data
        
        try:
            formatted_city = self.format_city_name(city_name)
            url = f"{self.BASE_URL}/{formatted_city}"
            
            logger.info(f"Scraping tidal data from {url}")
            response = self.session.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract date
            date_text = soup.find('div', string=re.compile(r'Tide Times for'))
            if not date_text:
                logger.error(f"Could not find date information for {city_name}")
                return None
            
            # Extract tide data from table
            tide_table = soup.find('table', {'class': 'table-bordered'})
            if not tide_table:
                logger.error(f"Could not find tide table for {city_name}")
                return None
            
            rows = soup.find_all('tr')[1:]  # Skip header row
            
            high_tides = []
            low_tides = []
            
            for row in rows:
                columns = soup.find_all('td')
                if len(columns) >= 3:
                    tide_type = columns[0].text.strip()
                    tide_time = columns[1].text.strip()
                    tide_height = columns[2].text.strip()
                    
                    if 'High Tide' in tide_type:
                        high_tides.append((tide_time, tide_height))
                    elif 'Low Tide' in tide_type:
                        low_tides.append((tide_time, tide_height))
            
            # Calculate tidal coefficient (simplified approach)
            # Extract heights from the tide_height strings
            heights = []
            for _, height_str in high_tides + low_tides:
                # Extract numeric height in meters
                match = re.search(r'(\d+\.\d+) m', height_str)
                if match:
                    heights.append(float(match.group(1)))
            
            if heights:
                min_height = min(heights)
                max_height = max(heights)
                height_range = max_height - min_height
                
                # Scale to a coefficient between 20 and 120 (common tidal coefficient range)
                coefficient = int(20 + (height_range * 100 / 10))  # Assuming max range is about 10m
                coefficient = min(120, max(20, coefficient))
            else:
                coefficient = 57  # Default value
            
            # Get the first high and low tide of the day
            high_tide_time = high_tides[0][0] if high_tides else 'N/A'
            low_tide_time = low_tides[0][0] if low_tides else 'N/A'
            
            tidal_data = {
                'coefficient': coefficient,
                'high_tide_time': high_tide_time,
                'low_tide_time': low_tide_time
            }
            
            # Cache the data
            cache_data(cache_key, tidal_data, 3600 * 6)  # Cache for 6 hours
            
            return tidal_data
            
        except Exception as e:
            logger.error(f"Error scraping tidal data for {city_name}: {str(e)}")
            return None
