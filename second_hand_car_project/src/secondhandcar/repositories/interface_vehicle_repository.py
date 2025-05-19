from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from uuid import UUID
from secondhandcar.models.car import Car # Assuming CRUD is primarily for Cars as per dataset

class IVehicleRepository(ABC):
    @abstractmethod
    def add_vehicle(self, vehicle: Car) -> None:
        pass

    @abstractmethod
    def get_vehicle_by_id(self, vehicle_id: UUID) -> Optional[Car]:
        pass

    @abstractmethod
    def get_all_vehicles(self) -> List[Car]:
        pass

    @abstractmethod
    def update_vehicle(self, vehicle: Car) -> None:
        pass

    @abstractmethod
    def delete_vehicle(self, vehicle_id: UUID) -> None:
        pass

    @abstractmethod
    def search_vehicles(self, criteria: Dict[str, Any]) -> List[Car]:
        pass
