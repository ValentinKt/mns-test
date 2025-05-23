from services.weather_service import WeatherService
from services.tidal_scraper import TidalScraperService

# Service instances
_weather_service = None
_tidal_service = None

def get_weather_service():
    """Get or create the weather service instance."""
    global _weather_service
    if _weather_service is None:
        _weather_service = WeatherService()
    return _weather_service

def get_tidal_service():
    """Get or create the tidal service instance."""
    global _tidal_service
    if _tidal_service is None:
        _tidal_service = TidalScraperService()
    return _tidal_service