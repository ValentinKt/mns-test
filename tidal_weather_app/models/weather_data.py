from datetime import datetime, timezone, date as dt_date
from models import get_db_connection

class WeatherData:
    """Model for storing weather data information."""
    
    def __init__(self, id=None, location_id=None, date=None, temperature=None, 
                 condition=None, wind_speed=None, sunrise=None, sunset=None, 
                 created_at=None, updated_at=None):
        self.id = id
        self.location_id = location_id
        self.date = date if isinstance(date, dt_date) else dt_date.fromisoformat(date) if date else None
        self.temperature = temperature
        self.condition = condition
        self.wind_speed = wind_speed
        self.sunrise = sunrise
        self.sunset = sunset
        self.created_at = created_at or datetime.now(timezone.utc)
        self.updated_at = updated_at or datetime.now(timezone.utc)
    
    def __repr__(self):
        return f'<WeatherData {self.date} for location {self.location_id}>'
    
    def to_dict(self):
        """Convert weather data object to dictionary."""
        return {
            'id': self.id,
            'location_id': self.location_id,
            'date': self.date.isoformat() if self.date else None,
            'temperature': self.temperature,
            'condition': self.condition,
            'wind_speed': self.wind_speed,
            'sunrise': self.sunrise,
            'sunset': self.sunset
        }
    
    @classmethod
    def query(cls):
        """Return a query object for the WeatherData model."""
        return WeatherDataQuery(cls)
    
    @classmethod
    def get_by_location_and_date(cls, location_id, date):
        """Get weather data for a specific location and date."""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if isinstance(date, dt_date):
            date_str = date.isoformat()
        else:
            date_str = date
            
        cursor.execute(
            "SELECT * FROM weather_data WHERE location_id = ? AND date = ?", 
            (location_id, date_str)
        )
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return cls(**dict(row))
        return None
    
    def save(self):
        """Save the weather data to the database."""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        now = datetime.now(timezone.utc)
        self.updated_at = now
        
        if self.id:
            # Update existing weather data
            cursor.execute(
                """UPDATE weather_data 
                   SET location_id = ?, date = ?, temperature = ?, condition = ?, 
                       wind_speed = ?, sunrise = ?, sunset = ?, updated_at = ? 
                   WHERE id = ?""",
                (self.location_id, self.date.isoformat(), self.temperature, self.condition, 
                 self.wind_speed, self.sunrise, self.sunset, now, self.id)
            )
        else:
            # Insert new weather data
            self.created_at = now
            cursor.execute(
                """INSERT INTO weather_data 
                   (location_id, date, temperature, condition, wind_speed, sunrise, sunset, created_at, updated_at) 
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (self.location_id, self.date.isoformat(), self.temperature, self.condition, 
                 self.wind_speed, self.sunrise, self.sunset, now, now)
            )
            self.id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        return self


class WeatherDataQuery:
    """Query builder for WeatherData model."""
    
    def __init__(self, model_class):
        self.model_class = model_class
        self.filters = []
    
    def filter_by(self, **kwargs):
        """Add a filter by keyword arguments."""
        for key, value in kwargs.items():
            if key == 'date' and isinstance(value, dt_date):
                value = value.isoformat()
            self.filters.append((f"{key} = ?", value))
        return self
    
    def first(self):
        """Execute the query and return the first result."""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM weather_data"
        params = []
        
        if self.filters:
            conditions = []
            for filter_args in self.filters:
                conditions.append(filter_args[0])
                params.append(filter_args[1])
            
            query += " WHERE " + " AND ".join(conditions)
        
        query += " LIMIT 1"
        cursor.execute(query, params)
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return self.model_class(**dict(row))
        return None