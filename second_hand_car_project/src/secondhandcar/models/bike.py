from .base_vehicle import BaseVehicle
from .vehicle_type import VehicleType

class Bike(BaseVehicle):
    def __init__(self, brand: str, model: str, year: int, price: float, bike_type: str = "Standard"):
        super().__init__(brand, model, year, price, VehicleType.BIKE)
        self._bike_type = bike_type # e.g., Mountain, Road, Hybrid

    @property
    def bike_type(self) -> str:
        return self._bike_type

    @bike_type.setter
    def bike_type(self, value: str):
        self._bike_type = value

    def get_wheels_needed(self) -> int:
        return 2

    @property
    def full_description(self) -> str:
        return f"{self.brand} {self.model} ({self.bike_type})"

    def __str__(self) -> str:
        base_str = super().__str__()
        return f"{base_str}, Type: {self.bike_type}"
