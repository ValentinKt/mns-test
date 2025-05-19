class FacilityFullError(Exception):
    """Custom exception for when a facility (Showroom, Garage) is full."""
    pass

class VehicleNotFoundError(Exception):
    """Custom exception for when a vehicle is not found."""
    pass

class InsufficientStockError(Exception):
    """Custom exception for when there is not enough stock of an item (e.g., spare parts)."""
    pass

class DataParsingError(Exception):
    """Custom exception for errors during data parsing."""
    pass
