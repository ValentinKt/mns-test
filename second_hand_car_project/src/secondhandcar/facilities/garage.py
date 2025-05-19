from typing import Dict
from .storage_facility import StorageFacility
from secondhandcar.models.vehicle_type import VehicleType

class Garage(StorageFacility):
    DEFAULT_CAPACITIES = {
        VehicleType.CAR: 50,
        VehicleType.BIKE: 7,
        VehicleType.SCOOTER: 10
    }
    def __init__(self, name: str = "Main Garage", capacities: Dict[VehicleType, int] = None):
        actual_capacities = capacities if capacities is not None else self.DEFAULT_CAPACITIES
        super().__init__(name, actual_capacities)
        print(f"Garage '{name}' initialized with capacities: {actual_capacities}")

    def display_for_repair(self):
        print(f"\n--- Vehicles for Repair in {self.name} ---")
        self.list_vehicles()
