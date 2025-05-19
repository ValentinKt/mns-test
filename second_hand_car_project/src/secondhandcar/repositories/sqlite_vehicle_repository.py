import sqlite3
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
import os
import pandas as pd # Make sure pandas is imported here

from secondhandcar.models.car import Car
from .interface_vehicle_repository import IVehicleRepository
from secondhandcar.utils.data_parser import parse_car_name # For initial load

class SQLiteVehicleRepository(IVehicleRepository):
    def __init__(self, db_filepath: str):
        self.db_filepath = db_filepath
        self._create_table_if_not_exists()

    def _get_connection(self):
        return sqlite3.connect(self.db_filepath)

    def _create_table_if_not_exists(self):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cars (
                id TEXT PRIMARY KEY,
                brand TEXT NOT NULL,
                model TEXT NOT NULL,
                year INTEGER NOT NULL,
                price REAL NOT NULL,
                km_driven INTEGER NOT NULL,
                fuel_type TEXT,
                transmission TEXT,
                owner_type TEXT,
                ecological_bonus_eligible BOOLEAN,
                is_sold BOOLEAN DEFAULT 0,
                is_available BOOLEAN DEFAULT 1 
            )
        """)
        conn.commit()
        conn.close()

    def add_vehicle(self, vehicle: Car) -> None:
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO cars (id, brand, model, year, price, km_driven, fuel_type, transmission, owner_type, ecological_bonus_eligible, is_sold, is_available)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                str(vehicle.id), vehicle.brand, vehicle.model, vehicle.year, vehicle.price,
                vehicle.km_driven, vehicle.fuel_type, vehicle.transmission, vehicle.owner_type,
                vehicle.ecological_bonus_eligible, vehicle.is_sold, vehicle.is_available
            ))
            conn.commit()
        except sqlite3.IntegrityError:
            conn.rollback()
            raise ValueError(f"Vehicle with ID {vehicle.id} already exists or another integrity constraint failed.")
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def get_vehicle_by_id(self, vehicle_id: UUID) -> Optional[Car]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM cars WHERE id = ?", (str(vehicle_id),))
        row = cursor.fetchone()
        conn.close()

        if row:
            car = Car(
                brand=row[1], model=row[2], year=row[3], price=row[4],
                km_driven=row[5], fuel_type=row[6], transmission=row[7],
                owner_type=row[8], ecological_bonus_eligible=bool(row[9])
            )
            car.id = UUID(row[0]) # Set the original ID
            car.is_sold = bool(row[10])
            car.is_available = bool(row[11])
            return car
        return None

    def get_all_vehicles(self) -> List[Car]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM cars")
        rows = cursor.fetchall()
        conn.close()

        cars = []
        for row in rows:
            car = Car(
                brand=row[1], model=row[2], year=row[3], price=row[4],
                km_driven=row[5], fuel_type=row[6], transmission=row[7],
                owner_type=row[8], ecological_bonus_eligible=bool(row[9])
            )
            car.id = UUID(row[0])
            car.is_sold = bool(row[10])
            car.is_available = bool(row[11])
            cars.append(car)
        return cars

    def update_vehicle(self, vehicle: Car) -> None:
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE cars
                SET brand = ?, model = ?, year = ?, price = ?, km_driven = ?, 
                    fuel_type = ?, transmission = ?, owner_type = ?, 
                    ecological_bonus_eligible = ?, is_sold = ?, is_available = ?
                WHERE id = ?
            """, (
                vehicle.brand, vehicle.model, vehicle.year, vehicle.price, vehicle.km_driven,
                vehicle.fuel_type, vehicle.transmission, vehicle.owner_type,
                vehicle.ecological_bonus_eligible, vehicle.is_sold, vehicle.is_available,
                str(vehicle.id)
            ))
            if cursor.rowcount == 0:
                raise ValueError(f"Vehicle with ID {vehicle.id} not found for update.")
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def delete_vehicle(self, vehicle_id: UUID) -> None:
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM cars WHERE id = ?", (str(vehicle_id),))
            if cursor.rowcount == 0:
                 raise ValueError(f"Vehicle with ID {vehicle_id} not found for deletion.")
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def search_vehicles(self, criteria: Dict[str, Any]) -> List[Car]:
        conn = self._get_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM cars WHERE 1=1"
        params = []

        for key, value in criteria.items():
            if key in ["brand", "model", "fuel_type", "transmission", "owner_type"]:
                query += f" AND {key} LIKE ?"
                params.append(f"%{value}%")
            elif key in ["year", "km_driven", "price"]:
                if isinstance(value, tuple) and len(value) == 2: 
                    query += f" AND {key} BETWEEN ? AND ?"
                    params.extend([value[0], value[1]])
                else:
                    query += f" AND {key} = ?"
                    params.append(value)
            elif key == "ecological_bonus_eligible":
                query += f" AND {key} = ?"
                params.append(1 if value else 0)
            elif key == "max_price":
                 query += f" AND price <= ?"
                 params.append(float(value))
            elif key == "min_year":
                 query += f" AND year >= ?"
                 params.append(int(value))

        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()
        conn.close()

        cars = []
        for row in rows:
            car = Car(
                brand=row[1], model=row[2], year=row[3], price=row[4],
                km_driven=row[5], fuel_type=row[6], transmission=row[7],
                owner_type=row[8], ecological_bonus_eligible=bool(row[9])
            )
            car.id = UUID(row[0])
            car.is_sold = bool(row[10])
            car.is_available = bool(row[11])
            cars.append(car)
        return cars

    def _is_table_empty(self, table_name: str) -> bool:
         conn = self._get_connection()
         cursor = conn.cursor()
         try:
             cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
             count = cursor.fetchone()[0]
             return count == 0
         except sqlite3.Error as e:
             print(f"Error checking if table {table_name} is empty: {e}")
             return True # Assume empty or non-existent if error occurs
         finally:
             conn.close()

    def load_from_csv(self, csv_filepath: str):
        """Loads data from a CSV file into the SQLite database."""
        if not self._is_table_empty("cars"):
            print(f"Table 'cars' is not empty. Skipping CSV load to avoid duplicates or overwriting.")
            return
        
        try:
            df = pd.read_csv(csv_filepath)
        except FileNotFoundError:
            print(f"CSV file not found: {csv_filepath}")
            return
        except Exception as e:
            print(f"Error reading CSV {csv_filepath}: {e}")
            return

        conn = self._get_connection()
        cursor = conn.cursor()
        loaded_count = 0
        skipped_count = 0

        for index, row_data in df.iterrows():
            try:
                brand, model_name = parse_car_name(str(row_data.get('name', '')))
                if brand == "Unknown" and model_name == "Unknown": # Skip if name parsing fails badly
                    print(f"Skipping row {index} due to unparsable name: {row_data.get('name', '')}")
                    skipped_count += 1
                    continue

                car_id = uuid4() 
                
                year = int(row_data['year'])
                price = float(row_data['selling_price'])
                km_driven = int(row_data['km_driven'])
                fuel_type = str(row_data['fuel'])
                transmission = str(row_data['transmission'])
                owner_type = str(row_data['owner'])
                ecological_bonus_eligible = fuel_type.upper() in ["CNG", "LPG", "ELECTRIC"]

                cursor.execute("""
                    INSERT INTO cars (id, brand, model, year, price, km_driven, fuel_type, transmission, owner_type, ecological_bonus_eligible, is_sold, is_available)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    str(car_id), brand, model_name, year, price, km_driven,
                    fuel_type, transmission, owner_type, ecological_bonus_eligible,
                    False, True 
                ))
                loaded_count += 1
            except KeyError as e:
                print(f"Skipping row {index} due to missing key: {e}. Row data: {row_data.to_dict()}")
                skipped_count +=1
            except ValueError as e:
                print(f"Skipping row {index} due to value error: {e}. Row data: {row_data.to_dict()}")
                skipped_count +=1
            except Exception as e:
                print(f"Skipping row {index} due to unexpected error: {e}. Row data: {row_data.to_dict()}")
                skipped_count +=1
        
        conn.commit()
        conn.close()
        print(f"Data loading from {csv_filepath} complete. Loaded: {loaded_count} rows, Skipped: {skipped_count} rows.")
