# SecondHandCar Information System

This project implements an information system for "SecondHandCar", a company that sells, buys, and repairs vehicles, including cars, bikes, and scooters.

## Features

- **Vehicle Management**:
  - Supports Cars, Bikes, and Scooters.
  - `full_description` property for vehicles (e.g., "Maruti 800 AC Petrol").
  - Ecological bonus eligibility for cars.
- **Facility Management**:
  - Showrooms and Garages with specific capacities for each vehicle type:
    - Car Showroom: 100 units
    - Car Garage (repair): 50 units
    - Bike Showroom: 20 units
    - Scooter Showroom: 10 units
    - Bike Garage (repair): 7 units
    - Scooter Garage (repair): 10 units
- **Transaction Management**:
  - Sales of vehicles.
  - Purchases of vehicles and spare parts.
  - Repair services, including spare part usage.
- **Reporting**:
  - Daily accounting reports for sales, repairs, and purchases.
- **Data Persistence**:
  - CRUD operations for used cars.
  - Supports data management via:
    - Pandas (using a CSV dataset).
    - SQLite database.
- **Modularity**:
  - Organized into models, facilities, transactions, repositories, services, and utilities.
  - Adherence to SOLID principles and use of inheritance.

## Project Structure

- `data/`: Contains the input CSV dataset (`car_dekho_details.csv`) and the SQLite database (`secondhandcar.db`).
- `src/secondhandcar/`: Main source code for the application.
  - `models/`: Defines data structures (Vehicle, Customer, SparePart, etc.).
  - `facilities/`: Manages physical spaces like Showroom and Garage.
  - `transactions/`: Represents financial and operational events (Sale, Repair, Purchase).
  - `repositories/`: Handles data storage and retrieval (Pandas, SQLite).
  - `services/`: Contains business logic (Inventory, Financial, Reporting).
  - `utils/`: Helper modules (TVA calculation, custom exceptions, data parsing).
  - `main.py`: Entry point and example usage of the system.

## Setup and Usage

1. **Prerequisites**:
    - Python 3.8+
    - `pandas` library (`pip install pandas`)

2. **Data**:
    - Place the `CAR DETAILS FROM CAR DEKHO.csv` file into the `data/` directory and rename it to `car_dekho_details.csv`.

3. **Running the Application**:
    - Execute `main.py` from the `src/secondhandcar/` directory:

      ```bash
      python src/secondhandcar/main.py
      ```

    - The `main.py` script demonstrates loading data, performing CRUD operations, and generating reports. It can be configured to use either the Pandas or SQLite repository.

## Design Principles

- **Abstraction**: `BaseVehicle` and `StorageFacility` provide common interfaces.
- **Inheritance**: `Car`, `Bike`, `Scooter` inherit from `BaseVehicle`. `Showroom`, `Garage` inherit from `StorageFacility`.
- **Encapsulation**: Attributes are generally private with property accessors.
- **Error Handling**: Custom exceptions are used for specific error conditions.
