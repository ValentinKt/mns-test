from abc import ABC, abstractmethod
from typing import Dict, List, Type
from secondhandcar.models.base_vehicle import BaseVehicle
from secondhandcar.models.vehicle_type import VehicleType
from secondhandcar.utils.custom_exceptions import FacilityFullError, VehicleNotFoundError

class StorageFacility(ABC):
    def __init__(self, name: str, capacities: Dict[VehicleType, int]):
        self._name = name
        self._capacities: Dict[VehicleType, int] = capacities
        self._vehicles_stored: Dict[VehicleType, List[BaseVehicle]] = {vt: [] for vt in VehicleType}

    @property
    def name(self) -> str:
        return self._name

    def add_vehicle(self, vehicle: BaseVehicle) -> None:
        vehicle_type = vehicle.vehicle_type
        if vehicle_type not in self._capacities:
            raise ValueError(f"Facility {self._name} does not support {vehicle_type.name}.")

        if len(self._vehicles_stored[vehicle_type]) >= self._capacities[vehicle_type]:
            raise FacilityFullError(f"{self._name} is full for {vehicle_type.name}s.")
        
        if vehicle in self._vehicles_stored[vehicle_type]:
            raise ValueError(f"Vehicle {vehicle.id} already in {self._name}.")

        self._vehicles_stored[vehicle_type].append(vehicle)
        vehicle.is_available = False # Mark as in facility, not for general sale
        print(f"{vehicle.vehicle_type.name} {vehicle.brand} {vehicle.model} added to {self._name}.")

    def remove_vehicle(self, vehicle: BaseVehicle) -> None:
        vehicle_type = vehicle.vehicle_type
        if vehicle_type not in self._vehicles_stored or vehicle not in self._vehicles_stored[vehicle_type]:
            raise VehicleNotFoundError(f"Vehicle {vehicle.id} not found in {self._name} for type {vehicle_type.name}.")
        
        self._vehicles_stored[vehicle_type].remove(vehicle)
        vehicle.is_available = True # Mark as available again, or handle based on context (e.g., sold)
        print(f"{vehicle.vehicle_type.name} {vehicle.brand} {vehicle.model} removed from {self._name}.")

    def list_vehicles(self) -> None:
        print(f"\nVehicles in {self._name}:")
        if not any(self._vehicles_stored.values()):
            print("  No vehicles currently stored.")
            return
        for vehicle_type, vehicles in self._vehicles_stored.items():
            if vehicles:
                print(f"  {vehicle_type.name}s ({len(vehicles)}/{self._capacities.get(vehicle_type, 0)}):")
                for v in vehicles:
                    print(f"    - {v}")
    
    def get_current_occupancy(self, vehicle_type: VehicleType) -> int:
        return len(self._vehicles_stored.get(vehicle_type, []))

    def get_capacity(self, vehicle_type: VehicleType) -> int:
        return self._capacities.get(vehicle_type, 0)

    def get_all_stored_vehicles(self) -> List[BaseVehicle]:
        all_vehicles = []
        for vehicle_list in self._vehicles_stored.values():
            all_vehicles.extend(vehicle_list)
        return all_vehicles
