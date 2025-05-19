import pandas as pd
from typing import List, Optional, Dict, Any
from uuid import UUID
import os

from secondhandcar.models.car import Car
from .interface_vehicle_repository import IVehicleRepository
from secondhandcar.utils.data_parser import parse_car_data_from_series, car_to_series

class PandasVehicleRepository(IVehicleRepository):
    def __init__(self, csv_filepath: str):
        self.filepath = csv_filepath
        self.df = self._load_data()

    def _load_data(self) -> pd.DataFrame:
        try:
            df = pd.read_csv(self.filepath)
            if 'id' not in df.columns:
                # Generate UUIDs if not present (for initial load from raw CSV)
                df['id'] = [str(UUID(int=i)) for i in range(len(df))] 
            else:
                # Ensure 'id' is string for consistency if loaded from a previously saved df
                df['id'] = df['id'].astype(str)
            df.set_index('id', inplace=True)
            return df
        except FileNotFoundError:
            # Create an empty DataFrame with expected columns if file doesn't exist
            columns = ['name', 'year', 'selling_price', 'km_driven', 'fuel', 
                       'seller_type', 'transmission', 'owner', 
                       'brand', 'model', 'ecological_bonus_eligible'] # Add derived/expected
            df = pd.DataFrame(columns=columns)
            df['id'] = [] # ensure id column exists
            df.set_index('id', inplace=True)
            return df
        except Exception as e:
            print(f"Error loading data from {self.filepath}: {e}")
            raise

    def _save_data(self) -> None:
        try:
            # Reset index to save 'id' as a column
            self.df.reset_index().to_csv(self.filepath, index=False)
        except Exception as e:
            print(f"Error saving data to {self.filepath}: {e}")
            raise

    def add_vehicle(self, vehicle: Car) -> None:
        if str(vehicle.id) in self.df.index:
            raise ValueError(f"Vehicle with ID {vehicle.id} already exists.")
        
        vehicle_series = car_to_series(vehicle)
        # Use loc to add a new row by index
        self.df.loc[str(vehicle.id)] = vehicle_series
        self._save_data()

    def get_vehicle_by_id(self, vehicle_id: UUID) -> Optional[Car]:
        vehicle_id_str = str(vehicle_id)
        if vehicle_id_str not in self.df.index:
            return None
        
        vehicle_series = self.df.loc[vehicle_id_str]
        return parse_car_data_from_series(vehicle_series, vehicle_id_str)


    def get_all_vehicles(self) -> List[Car]:
        cars = []
        for vehicle_id_str, row in self.df.iterrows():
            car = parse_car_data_from_series(row, vehicle_id_str)
            if car:
                cars.append(car)
        return cars

    def update_vehicle(self, vehicle: Car) -> None:
        vehicle_id_str = str(vehicle.id)
        if vehicle_id_str not in self.df.index:
            raise ValueError(f"Vehicle with ID {vehicle.id} not found.")
        
        vehicle_series = car_to_series(vehicle)
        self.df.loc[vehicle_id_str] = vehicle_series
        self._save_data()

    def delete_vehicle(self, vehicle_id: UUID) -> None:
        vehicle_id_str = str(vehicle_id)
        if vehicle_id_str not in self.df.index:
            raise ValueError(f"Vehicle with ID {vehicle_id} not found.")
        
        self.df.drop(index=vehicle_id_str, inplace=True)
        self._save_data()

    def search_vehicles(self, criteria: Dict[str, Any]) -> List[Car]:
        results_df = self.df.copy()
        for key, value in criteria.items():
            if key in results_df.columns:
                if isinstance(value, str): # Case-insensitive search for strings
                    results_df = results_df[results_df[key].astype(str).str.contains(value, case=False, na=False)]
                elif isinstance(value, (int, float)):
                    # For numeric, allow range or exact match
                    if isinstance(value, tuple) and len(value) == 2: # range (min, max)
                        results_df = results_df[(results_df[key] >= value[0]) & (results_df[key] <= value[1])]
                    else: # exact match
                        results_df = results_df[results_df[key] == value]
                elif isinstance(value, bool):
                     results_df = results_df[results_df[key] == value]
            elif key == "max_price":
                 results_df = results_df[results_df["selling_price"] <= float(value)]
            elif key == "min_year":
                 results_df = results_df[results_df["year"] >= int(value)]
            # Add more specific criteria handling if needed

        cars = []
        for vehicle_id_str, row in results_df.iterrows():
            car = parse_car_data_from_series(row, vehicle_id_str)
            if car:
                cars.append(car)
        return cars
