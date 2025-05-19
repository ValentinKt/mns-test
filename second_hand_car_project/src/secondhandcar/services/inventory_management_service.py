from secondhandcar.models.base_vehicle import BaseVehicle
from secondhandcar.facilities.showroom import Showroom
from secondhandcar.facilities.garage import Garage
from secondhandcar.repositories.interface_vehicle_repository import IVehicleRepository
from secondhandcar.utils.custom_exceptions import VehicleNotFoundError

class InventoryManagementService:
    def __init__(self, showroom: Showroom, garage: Garage, vehicle_repository: IVehicleRepository):
        self._showroom = showroom
        self._garage = garage
        self._vehicle_repository = vehicle_repository # For managing the master list of vehicles

    def add_vehicle_to_showroom(self, vehicle: BaseVehicle):
        # Assuming vehicle is first added to repository if it's a new purchase
        # Then moved to showroom
        if not self._vehicle_repository.get_vehicle_by_id(vehicle.id):
             # This check might be redundant if vehicles are always in repo first
            raise VehicleNotFoundError(f"Vehicle {vehicle.id} not in master inventory.")
        
        self._showroom.add_vehicle(vehicle)
        vehicle.is_available = True # Specifically for sale in showroom
        self._vehicle_repository.update_vehicle(vehicle) # Update master status

    def remove_vehicle_from_showroom(self, vehicle: BaseVehicle):
        self._showroom.remove_vehicle(vehicle)
        # Vehicle state (is_available, is_sold) should be updated by calling service (e.g., SalesService)
        # Here, we just reflect it's no longer in showroom physically.
        # If it's not sold, it might go back to a general pool or another status.
        # For simplicity, SalesService will handle the final state update in repository.

    def add_vehicle_to_garage(self, vehicle: BaseVehicle):
        if not self._vehicle_repository.get_vehicle_by_id(vehicle.id):
            raise VehicleNotFoundError(f"Vehicle {vehicle.id} not in master inventory.")
        
        self._garage.add_vehicle(vehicle)
        vehicle.is_available = False # In repair, not available for sale
        self._vehicle_repository.update_vehicle(vehicle)

    def remove_vehicle_from_garage(self, vehicle: BaseVehicle):
        self._garage.remove_vehicle(vehicle)
        vehicle.is_available = True # Assuming it's repaired and ready
        self._vehicle_repository.update_vehicle(vehicle)

    def list_showroom_vehicles(self):
        self._showroom.display_for_sale()

    def list_garage_vehicles(self):
        self._garage.display_for_repair()

    def get_all_company_vehicles(self) -> list[BaseVehicle]:
        return self._vehicle_repository.get_all_vehicles()
