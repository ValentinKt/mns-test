import sys
import os
from uuid import UUID
from datetime import date, datetime # Added datetime for report_date default

# --- Start of sys.path modification ---
# Get the directory of the current script (main.py)
# e.g., /path/to/second_hand_car_project/src/secondhandcar
script_dir = os.path.dirname(os.path.abspath(__file__))

# Get the 'src' directory (parent of 'secondhandcar' directory)
# e.g., /path/to/second_hand_car_project/src
src_dir = os.path.dirname(script_dir)

# Add 'src' directory to sys.path if it's not already there
# This allows imports like 'from secondhandcar.models ...' to work correctly
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)
# --- End of sys.path modification ---

from secondhandcar.models import Car, Customer, VehicleType, Bike, Scooter, BaseVehicle, SparePart
from secondhandcar.repositories import PandasVehicleRepository, SQLiteVehicleRepository, IVehicleRepository
from secondhandcar.facilities import Showroom, Garage
from secondhandcar.services import InventoryManagementService, FinancialTransactionService, ReportingService
from secondhandcar.utils.data_parser import parse_car_name
from secondhandcar.transactions.transaction import Transaction # For type hinting in FinancialTransactionService

# Configuration
# Correctly determine project_root and then data_dir
project_root_dir = os.path.dirname(src_dir) # This should be second_hand_car_project
DATA_DIR = os.path.join(project_root_dir, 'data')

CSV_FILE = os.path.join(DATA_DIR, 'car_dekho_details.csv') # Original CSV for loading
PANDAS_REPO_CSV_FILE = os.path.join(DATA_DIR, 'pandas_repo_cars.csv') # CSV for Pandas repo state
DB_FILE = os.path.join(DATA_DIR, 'secondhandcar.db')

USE_SQLITE = True # Set to False to use Pandas repository

def setup_repositories() -> IVehicleRepository:
    if USE_SQLITE:
        print("Using SQLite Repository")
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)
        
        repo = SQLiteVehicleRepository(DB_FILE)
        # The load_from_csv method now has its own check for emptiness.
        # We call it unconditionally here, and it will decide if loading is needed.
        print(f"Attempting to load initial data into SQLite from {CSV_FILE} if table is empty...")
        if os.path.exists(CSV_FILE):
            repo.load_from_csv(CSV_FILE)
        else:
            print(f"Warning: Original CSV file {CSV_FILE} not found. Cannot initialize SQLite DB if empty.")
        return repo
    else:
        # ... (Pandas part remains the same) ...
        print("Using Pandas Repository")
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)
        if not os.path.exists(PANDAS_REPO_CSV_FILE) and os.path.exists(CSV_FILE):
            import shutil
            try:
                shutil.copy(CSV_FILE, PANDAS_REPO_CSV_FILE)
                print(f"Initialized Pandas repository file from {CSV_FILE}")
            except Exception as e:
                print(f"Error copying {CSV_FILE} to {PANDAS_REPO_CSV_FILE}: {e}")

        elif not os.path.exists(PANDAS_REPO_CSV_FILE):
             print(f"Warning: Pandas repository file {PANDAS_REPO_CSV_FILE} not found. Starting with an empty repository.")
        
        return PandasVehicleRepository(PANDAS_REPO_CSV_FILE)


def main():
    print("Initializing SecondHandCar System...")

    # Setup Repository
    vehicle_repo = setup_repositories()

    # Setup Facilities
    showroom = Showroom()
    garage = Garage()

    # Setup Services
    inventory_service = InventoryManagementService(showroom, garage, vehicle_repo)
    financial_service = FinancialTransactionService(vehicle_repo)
    reporting_service = ReportingService(financial_service)

    # --- DEMONSTRATE FUNCTIONALITY ---

    print("\n--- Loading vehicles into Showroom ---")
    all_cars_in_repo = vehicle_repo.get_all_vehicles()
    
    cars_for_showroom_count = 0
    for car_obj in all_cars_in_repo:
        if not isinstance(car_obj, Car): # Ensure it's a Car object for this demo part
            continue
        if cars_for_showroom_count >= 5:
            break
        if car_obj.is_available and not car_obj.is_sold:
            try:
                is_in_facility = any(car_obj.id == v.id for v in showroom.get_all_stored_vehicles()) or \
                                 any(car_obj.id == v.id for v in garage.get_all_stored_vehicles())
                if not is_in_facility:
                    inventory_service.add_vehicle_to_showroom(car_obj)
                    cars_for_showroom_count += 1
            except Exception as e:
                print(f"Could not add {car_obj.brand} {car_obj.model} to showroom: {e}")
    
    inventory_service.list_showroom_vehicles()

    print("\n--- CRUD Operations Demo ---")
    
    new_car_details = {
        "brand": "Tesla", "model": "Model S", "year": 2021, "price": 75000.00,
        "km_driven": 15000, "fuel_type": "Electric", "transmission": "Automatic",
        "owner_type": "First Owner", "ecological_bonus_eligible": True
    }
    created_car = None
    try:
        created_car_obj = Car(**new_car_details)
        vehicle_repo.add_vehicle(created_car_obj)
        created_car = created_car_obj # Assign if successful
        print(f"CREATED: {created_car.full_description} with ID {created_car.id}")
    except Exception as e:
        print(f"Error creating car: {e}")

    if created_car:
        read_car = vehicle_repo.get_vehicle_by_id(created_car.id)
        if read_car:
            print(f"READ: {read_car.full_description}, Price: {read_car.price}")
            read_car.price = 72000.00
            read_car.km_driven = 16000
            vehicle_repo.update_vehicle(read_car)
            print(f"UPDATED: {read_car.full_description}, New Price: {read_car.price}")
        else:
            print(f"Could not read car with ID {created_car.id}")

    print("\nSearching for 'Maruti' cars...")
    search_criteria = {"brand": "Maruti", "max_price": 500000}
    found_cars = vehicle_repo.search_vehicles(search_criteria)
    print(f"Found {len(found_cars)} Maruti cars under 500,000:")
    for i, car_item in enumerate(found_cars):
        if i < 3 :
             print(f"  - {car_item.full_description}, Price: {car_item.price}")

    print("\n--- Sales Transaction Demo ---")
    customer1 = Customer(last_name="Doe", email="john.doe@example.com", first_name="John")
    
    car_to_sell = None
    if created_car:
        car_to_sell_candidate = vehicle_repo.get_vehicle_by_id(created_car.id)
        if car_to_sell_candidate and not car_to_sell_candidate.is_sold:
            car_to_sell = car_to_sell_candidate
            # If it was in showroom, remove it
            if any(v.id == car_to_sell.id for v in showroom.get_all_stored_vehicles()):
                inventory_service.remove_vehicle_from_showroom(car_to_sell)


    if not car_to_sell:
        showroom_vehicles = showroom.get_all_stored_vehicles()
        if showroom_vehicles:
            # Find first car in showroom that is not the one we might have just created/sold
            for v_in_showroom in showroom_vehicles:
                if isinstance(v_in_showroom, Car) and not v_in_showroom.is_sold:
                    if created_car and v_in_showroom.id == created_car.id:
                        continue # Skip if it's the one we tried above
                    car_to_sell = v_in_showroom
                    inventory_service.remove_vehicle_from_showroom(car_to_sell)
                    break
    
    if car_to_sell and not car_to_sell.is_sold:
        try:
            financial_service.record_sale(car_to_sell, customer1, car_to_sell.price)
        except Exception as e:
            print(f"Error selling car {car_to_sell.id}: {e}")
    else:
        print("No suitable car available for sale demo or chosen car already sold.")

    print("\n--- Spare Part Purchase Demo ---")
    financial_service.record_spare_part_purchase("Brake Pads", "BP123", 50.0, 10, "Parts Inc.")
    financial_service.record_spare_part_purchase("Oil Filter", "OF456", 15.0, 20, "Filters Co.")
    print("Current spare parts stock:")
    for part in financial_service.get_spare_parts_stock():
        print(f"  - {part}")

    print("\n--- Repair Transaction Demo ---")
    car_for_repair = None
    # Find a car that is not sold and not the one just sold (if any)
    available_for_repair_candidates = [c for c in vehicle_repo.get_all_vehicles() if isinstance(c, Car) and not c.is_sold]
    if car_to_sell: # Exclude the car that was just sold
        available_for_repair_candidates = [c for c in available_for_repair_candidates if c.id != car_to_sell.id]
    
    if available_for_repair_candidates:
        car_for_repair = available_for_repair_candidates[0]

    if car_for_repair:
        try:
            inventory_service.add_vehicle_to_garage(car_for_repair)
            print(f"Vehicle {car_for_repair.id} moved to garage for repair.")
            financial_service.record_repair(car_for_repair, customer1, "Oil change and brake check", 150.0, ["BP123", "OF456"])
            inventory_service.remove_vehicle_from_garage(car_for_repair)
            print(f"Vehicle {car_for_repair.id} repair complete and removed from garage.")
        except Exception as e:
            print(f"Error during repair demo for {car_for_repair.id}: {e}")
            if any(v.id == car_for_repair.id for v in garage.get_all_stored_vehicles()):
                inventory_service.remove_vehicle_from_garage(car_for_repair)
    else:
        print("No suitable car found for repair demo.")

    inventory_service.list_garage_vehicles()

    print("\n--- Reporting Demo ---")
    daily_report = reporting_service.generate_daily_report(datetime.now().date()) # Use datetime.now().date()
    print(daily_report)

    print("\n--- Other Vehicle Types Demo ---")
    bike1 = Bike(brand="Giant", model="Defy", year=2022, price=1200.00, bike_type="Road")
    scooter1 = Scooter(brand="Vespa", model="Primavera", year=2023, price=3500.00, color="Red", engine_cc=150)
    
    print(bike1)
    print(scooter1)

    try:
        # Bikes and Scooters are not managed by the current IVehicleRepository (Car-focused)
        # So, we add them directly to the showroom for this demo.
        # A more complete system would have repositories for all vehicle types or a generic one.
        showroom.add_vehicle(bike1)
        showroom.add_vehicle(scooter1)
        print(f"Added {bike1.brand} and {scooter1.brand} directly to showroom.")
    except Exception as e:
            print(f"Error adding bike/scooter to showroom: {e}")

    inventory_service.list_showroom_vehicles()

    # Example of deleting the created car if it exists and wasn't sold
    if created_car and vehicle_repo.get_vehicle_by_id(created_car.id):
        car_to_delete = vehicle_repo.get_vehicle_by_id(created_car.id)
        if car_to_delete and not car_to_delete.is_sold : # only delete if not sold
            try:
                vehicle_repo.delete_vehicle(created_car.id)
                print(f"DELETED (end of demo): {created_car.full_description}")
            except Exception as e:
                print(f"Error deleting car {created_car.id} at end of demo: {e}")


    print("\nSecondHandCar System Demo Finished.")

if __name__ == "__main__":
    main()
