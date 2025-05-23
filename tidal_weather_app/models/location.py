from datetime import datetime, timezone, date as dt_date
from models import get_db_connection

class Location:
    """Model for storing location information."""
    
    def __init__(self, id=None, name=None, latitude=None, longitude=None, 
                 description=None, timezone="UTC", created_at=None, updated_at=None):
        self.id = id
        self.name = name
        self.latitude = latitude
        self.longitude = longitude
        self.description = description
        self.timezone = timezone
        self.created_at = created_at or datetime.now(timezone.utc)
        self.updated_at = updated_at or datetime.now(timezone.utc)
    
    def __repr__(self):
        return f'<Location {self.name}>'
    
    def to_dict(self):
        """Convert location object to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'description': self.description,
            'timezone': self.timezone
        }
    
    @classmethod
    def query(cls):
        """Return a query object for the Location model."""
        return LocationQuery(cls)
    
    @classmethod
    def get_all(cls):
        """Get all locations from the database."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM locations")
        rows = cursor.fetchall()
        conn.close()
        
        return [cls(**dict(row)) for row in rows]
    
    @classmethod
    def get_by_id(cls, location_id):
        """Get a location by ID."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM locations WHERE id = ?", (location_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return cls(**dict(row))
        return None
    
    def save(self):
        """Save the location to the database."""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        now = datetime.now(timezone.utc)
        self.updated_at = now
        
        if self.id:
            # Update existing location
            cursor.execute(
                """UPDATE locations 
                   SET name = ?, latitude = ?, longitude = ?, description = ?, 
                       timezone = ?, updated_at = ? 
                   WHERE id = ?""",
                (self.name, self.latitude, self.longitude, self.description, 
                 self.timezone, now, self.id)
            )
        else:
            # Insert new location
            self.created_at = now
            cursor.execute(
                """INSERT INTO locations 
                   (name, latitude, longitude, description, timezone, created_at, updated_at) 
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (self.name, self.latitude, self.longitude, self.description, 
                 self.timezone, now, now)
            )
            self.id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        return self


class LocationQuery:
    """Query builder for Location model."""
    
    def __init__(self, model_class):
        self.model_class = model_class
        self.filters = []
    
    def filter(self, *args):
        """Add a filter to the query."""
        self.filters.append(args)
        return self
    
    def filter_by(self, **kwargs):
        """Add a filter by keyword arguments."""
        for key, value in kwargs.items():
            self.filters.append((f"{key} = ?", value))
        return self
    
    def all(self):
        """Execute the query and return all results."""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM locations"
        params = []
        
        if self.filters:
            conditions = []
            for filter_args in self.filters:
                if isinstance(filter_args[0], str):
                    conditions.append(filter_args[0])
                    if len(filter_args) > 1:
                        params.append(filter_args[1])
                else:
                    # Handle SQLAlchemy-style filter expressions
                    field_name = filter_args[0].key
                    op = filter_args[1]
                    value = filter_args[2]
                    
                    if op == 'ilike':
                        conditions.append(f"{field_name} LIKE ?")
                        params.append(value)
                    else:
                        conditions.append(f"{field_name} = ?")
                        params.append(value)
            
            query += " WHERE " + " AND ".join(conditions)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        return [self.model_class(**dict(row)) for row in rows]
    
    def first(self):
        """Execute the query and return the first result."""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM locations"
        params = []
        
        if self.filters:
            conditions = []
            for filter_args in self.filters:
                if isinstance(filter_args[0], str):
                    conditions.append(filter_args[0])
                    if len(filter_args) > 1:
                        params.append(filter_args[1])
                else:
                    # Handle SQLAlchemy-style filter expressions
                    field_name = filter_args[0].key
                    op = filter_args[1]
                    value = filter_args[2]
                    
                    if op == 'ilike':
                        conditions.append(f"{field_name} LIKE ?")
                        params.append(value)
                    else:
                        conditions.append(f"{field_name} = ?")
                        params.append(value)
            
            query += " WHERE " + " AND ".join(conditions)
        
        query += " LIMIT 1"
        cursor.execute(query, params)
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return self.model_class(**dict(row))
        return None