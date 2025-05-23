#!/usr/bin/env python3
"""
Script to search for cities in the SQLite database and fetch weather data from OpenWeatherMap.
"""

import sqlite3
import argparse
import requests
import json
import sys
from pathlib import Path
from bs4 import BeautifulSoup
import re
from datetime import datetime

# Define paths
BASE_DIR = Path(__file__).resolve().parent.parent
DB_FILE = BASE_DIR / 'data' / 'cities.db'

def search_city(name, country=None, limit=10):
    """
    Search for cities by name in the SQLite database.
    
    Args:
        name (str): City name to search for
        country (str, optional): Two-letter country code
        limit (int): Maximum number of results to return
        
    Returns:
        list: List of matching cities
    """
    if not DB_FILE.exists():
        print(f"Error: Database file not found at {DB_FILE}")
        print("Please run create_cities_db.py first to create the database.")
        sys.exit(1)
    
    conn = sqlite3.connect(DB_FILE)
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

def fetch_weather_data(city_id):
    """
    Fetch weather data from OpenWeatherMap website.
    
    Args:
        city_id (int): OpenWeatherMap city ID
        
    Returns:
        dict: Weather data or None if failed
    """
    url = f"https://openweathermap.org/city/{city_id}"
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return parse_weather_html(response.text, city_id)
    except requests.RequestException as e:
        print(f"Error fetching weather data: {e}")
        return None

def parse_weather_html(html_content, city_id):
    """
    Parse weather data from HTML content.
    
    Args:
        html_content (str): HTML content from OpenWeatherMap website
        city_id (int): City ID for reference
        
    Returns:
        dict: Structured weather data
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find the weather widget section
    weather_widget = soup.select_one("#weather-widget > div.section-content")
    
    if not weather_widget:
        print("Error: Could not find weather widget in HTML content")
        return None
    
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
        'pressure': weather_details['pressure'],
        'humidity': weather_details['humidity'],
        'uv': weather_details['uv'],
        'dew_point': weather_details['dew_point'],
        'visibility': weather_details['visibility'],
        'fetched_at': datetime.now().isoformat()
    }
    
    return weather_data

def display_weather(weather_data):
    """Display weather data in a formatted way."""
    if not weather_data:
        print("No weather data available.")
        return
    
    print("\n" + "="*50)
    print(f"Weather for {weather_data['city_country']}")
    print(f"Retrieved at: {weather_data['date_time']}")
    print("="*50)
    
    print(f"Temperature: {weather_data['temperature']}")
    print(f"Conditions: {weather_data['description']}")
    print(f"Wind: {weather_data['wind']}")
    print(f"Pressure: {weather_data['pressure']}")
    print(f"Humidity: {weather_data['humidity']}")
    print(f"UV Index: {weather_data['uv']}")
    print(f"Dew Point: {weather_data['dew_point']}")
    print(f"Visibility: {weather_data['visibility']}")
    print("="*50 + "\n")

def main():
    """Main function to run the script."""
    parser = argparse.ArgumentParser(description='Search for cities and fetch weather data')
    parser.add_argument('city', help='City name to search for')
    parser.add_argument('-c', '--country', help='Two-letter country code (optional)')
    parser.add_argument('-l', '--limit', type=int, default=10, help='Maximum number of search results')
    parser.add_argument('-i', '--id', type=int, help='Directly use city ID instead of searching')
    parser.add_argument('-j', '--json', action='store_true', help='Output in JSON format')
    
    args = parser.parse_args()
    
    if args.id:
        # Directly fetch weather using city ID
        weather_data = fetch_weather_data(args.id)
        if weather_data:
            if args.json:
                print(json.dumps(weather_data, indent=2))
            else:
                display_weather(weather_data)
        else:
            print(f"Could not fetch weather data for city ID {args.id}")
    else:
        # Search for city first
        cities = search_city(args.city, args.country, args.limit)
        
        if not cities:
            print(f"No cities found matching '{args.city}'")
            return
        
        if len(cities) == 1 or args.limit == 1:
            # If only one city found or limit is 1, fetch weather directly
            city = cities[0]
            print(f"Found city: {city['name']}, {city['country']} (ID: {city['id']})")
            weather_data = fetch_weather_data(city['id'])
            
            if weather_data:
                if args.json:
                    print(json.dumps(weather_data, indent=2))
                else:
                    display_weather(weather_data)
            else:
                print(f"Could not fetch weather data for {city['name']}")
        else:
            # Display list of cities for selection
            print(f"Found {len(cities)} cities matching '{args.city}':")
            for i, city in enumerate(cities, 1):
                state_info = f", {city['state']}" if city['state'] else ""
                print(f"{i}. {city['name']}{state_info}, {city['country']} (ID: {city['id']})")
            
            try:
                choice = int(input("\nEnter the number of the city to fetch weather for (0 to exit): "))
                if 1 <= choice <= len(cities):
                    selected_city = cities[choice-1]
                    weather_data = fetch_weather_data(selected_city['id'])
                    
                    if weather_data:
                        if args.json:
                            print(json.dumps(weather_data, indent=2))
                        else:
                            display_weather(weather_data)
                    else:
                        print(f"Could not fetch weather data for {selected_city['name']}")
                elif choice == 0:
                    print("Exiting...")
                else:
                    print("Invalid selection.")
            except ValueError:
                print("Invalid input. Please enter a number.")

if __name__ == "__main__":
    main()
