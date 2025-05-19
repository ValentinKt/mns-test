from typing import Tuple, Optional, Dict, Any
from uuid import UUID
import pandas as pd
from secondhandcar.models.car import Car
from secondhandcar.utils.custom_exceptions import DataParsingError

def parse_car_name(name_field: str) -> Tuple[str, str]:
    """
    Parses the 'name' field from the CSV into brand and model.
    Assumes the first word is the brand.
    """
    if not name_field or not isinstance(name_field, str):
        # raise DataParsingError("Name field is empty or not a string.")
        return "Unknown", "Unknown" # Or handle as error
    parts = name_field.split(" ", 1)
    brand = parts[0]
    model = parts[1] if len(parts) > 1 else "Unknown"
    return brand, model

def parse_car_data_from_series(row: pd.Series, vehicle_id_str: Optional[str] = None) -> Optional[Car]:
    """
    Parses a pandas Series (a row from DataFrame) into a Car object.
    """
    try:
        # Use 'brand' and 'model' if they exist (e.g. from a processed DataFrame)
        # Otherwise, parse from 'name'
        if 'brand' in row.index and 'model' in row.index and pd.notna(row['brand']) and pd.notna(row['model']):
            brand = str(row['brand'])
            model_name = str(row['model'])
        elif 'name' in row.index and pd.notna(row['name']):
            brand, model_name = parse_car_name(str(row['name']))
        else: # Not enough info to create a car
            return None


        year = int(row['year'])
        price = float(row['selling_price'])
        km_driven = int(row['km_driven'])
        fuel_type = str(row['fuel'])
        transmission = str(row['transmission'])
        owner_type = str(row['owner'])
        
        # Ecological bonus: if column exists, use it, otherwise infer
        if 'ecological_bonus_eligible' in row.index and pd.notna(row['ecological_bonus_eligible']):
            eco_bonus = bool(row['ecological_bonus_eligible'])
        else:
            eco_bonus = fuel_type.upper() in ["CNG", "LPG", "ELECTRIC"]

        car = Car(
            brand=brand, model=model_name, year=year, price=price,
            km_driven=km_driven, fuel_type=fuel_type, transmission=transmission,
            owner_type=owner_type, ecological_bonus_eligible=eco_bonus
        )
        
        if vehicle_id_str: # If ID is passed (e.g. from DataFrame index)
            car.id = UUID(vehicle_id_str)
        
        # Handle is_sold and is_available if present in the Series
        if 'is_sold' in row.index and pd.notna(row['is_sold']):
            car.is_sold = bool(row['is_sold'])
        if 'is_available' in row.index and pd.notna(row['is_available']):
            car.is_available = bool(row['is_available'])
            
        return car
    except Exception as e:
        # print(f"Error parsing car data for row {row.name if hasattr(row, 'name') else 'Unknown_ID'}: {e}")
        # print(f"Row data: {row.to_dict()}")
        # Depending on strictness, either return None or raise DataParsingError
        return None


def car_to_series(car: Car) -> pd.Series:
    """Converts a Car object to a pandas Series for DataFrame storage."""
    # 'name' field for compatibility with original CSV structure, though brand/model are preferred
    name = f"{car.brand} {car.model}"
    
    data = {
        'name': name, # Original combined name
        'brand': car.brand,
        'model': car.model,
        'year': car.year,
        'selling_price': car.price,
        'km_driven': car.km_driven,
        'fuel': car.fuel_type, # Match CSV column name
        'seller_type': "Dealer", # Default or could be another attribute
        'transmission': car.transmission,
        'owner': car.owner_type, # Match CSV column name
        'ecological_bonus_eligible': car.ecological_bonus_eligible,
        'is_sold': car.is_sold,
        'is_available': car.is_available
        # id is the index, so not included here
    }
    return pd.Series(data)
