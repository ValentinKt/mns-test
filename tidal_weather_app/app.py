from flask import Flask, render_template, request, jsonify
from models import Location, WeatherData, TidalData # Ensure TidalData is imported
from datetime import date
import logging
import os
import sqlite3
from pathlib import Path
from services.weather_service import WeatherService
from services.tidal_api import TidalAPIService # Ensure TidalAPIService is imported
import logging_config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging_config.setup_logging()

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.urandom(24) # For flash messages

# Set up paths
app_dir = os.path.dirname(os.path.abspath(__file__))
app.config['DATA_DIR'] = os.path.join(app_dir, 'data')
app.config['DB_FILE'] = os.path.join(app.config['DATA_DIR'], 'cities.db')

# Initialize services
weather_service = WeatherService(app.config['DB_FILE'])
tidal_service = TidalAPIService() # Ensure tidal_service is initialized

# Routes
@app.route('/')
def index():
    """Render the main page with weather information."""
    location_id = request.args.get('location_id', 1, type=int)
    search_query = request.args.get('search', '')
    
    # Get location data
    if search_query:
        # Search for locations matching the query
        locations = Location.query().filter_by(name=search_query).all()
        if not locations:
            # If no results, get all locations
            locations = Location.query().all()
    else:
        locations = Location.query().all()
    
    selected_location = Location.get_by_id(location_id) or (locations[0] if locations else None)
    
    if not selected_location:
        return render_template(
            'index.html',
            locations=[],
            selected_location=None,
            weather_data=None,
            tidal_data=None, # Add tidal_data here for the None case
            search_query=search_query
        )
    
    # Get today's weather data for the selected location
    weather_data = WeatherData.query().filter_by(
        location_id=selected_location.id,
        date=date.today()
    ).first()
    
    # If no weather data exists in the database, fetch from API
    if not weather_data:
        # Use the weather service to fetch weather data
        city_data = weather_service.get_city_by_id(selected_location.id)
        if city_data:
            weather_data_dict = weather_service.fetch_weather_data(selected_location.id)
            
            if weather_data_dict:
                # Save to database
                weather_data = WeatherData(
                    location_id=selected_location.id,
                    date=date.today(),
                    temperature=weather_data_dict.get('temperature_value', 0),
                    condition=weather_data_dict.get('description', 'Unknown'),
                    wind_speed=weather_data_dict.get('wind_speed', 0),
                    sunrise=weather_data_dict.get('sunrise', ''),
                    sunset=weather_data_dict.get('sunset', '')
                )
                weather_data.save()
    
    # Get today's tidal data for the selected location
    tidal_data = TidalData.get_by_location_and_date(selected_location.id, date.today())
    
    # If no tidal data exists in the database, fetch using the service
    if not tidal_data and selected_location:
        tidal_data_dict = tidal_service.get_tidal_data(
            selected_location.latitude,
            selected_location.longitude,
            selected_location.id,
            selected_location.name # Pass city_name for scraper fallback
        )
        if tidal_data_dict:
            tidal_data = TidalData(
                location_id=selected_location.id,
                date=date.today(),
                coefficient=tidal_data_dict.get('coefficient'),
                high_tide_time=tidal_data_dict.get('high_tide_time'),
                low_tide_time=tidal_data_dict.get('low_tide_time')
            )
            tidal_data.save()
            # Re-fetch from DB to have a consistent object type if needed, or use the dict directly
            # For simplicity, we'll assume the object created is sufficient for the template

    return render_template(
        'index.html',
        locations=locations,
        selected_location=selected_location,
        weather_data=weather_data,
        tidal_data=tidal_data,  # Pass tidal_data to the template
        search_query=search_query
    )

@app.route('/api/search')
def search_cities():
    """API endpoint to search for cities."""
    query = request.args.get('q', '')
    if not query or len(query) < 2:
        return jsonify([])
    
    cities = weather_service.search_cities(query)
    return jsonify(cities)

@app.route('/api/import_city/<int:city_id>', methods=['POST'])
def import_city(city_id):
    """API endpoint to import a city from cities to locations."""
    success = weather_service.import_city_to_locations(city_id)
    
    if success:
        return jsonify({'status': 'success', 'message': 'City imported successfully'})
    else:
        return jsonify({'status': 'error', 'message': 'Failed to import city'}), 400

@app.route('/api/import_cities_by_country', methods=['POST'])
def import_cities_by_country():
    """API endpoint to import cities from a specific country."""
    data = request.get_json(silent=True) or {}
    country_code = data.get('country_code', '')
    limit = data.get('limit', 10)
    
    if not country_code:
        return jsonify({'status': 'error', 'message': 'Country code is required'}), 400
    
    count = weather_service.import_cities_by_country(country_code, limit)
    
    return jsonify({
        'status': 'success', 
        'message': f'Imported {count} cities from {country_code}'
    })

if __name__ == '__main__':
    app.run(debug=True)
