from .base_vehicle import BaseVehicle
from .vehicle_type import VehicleType

class Scooter(BaseVehicle):
    def __init__(self, brand: str, model: str, year: int, price: float, color: str, engine_cc: int = 50):
        super().__init__(brand, model, year, price, VehicleType.SCOOTER)
        self._color: str = color
        self._engine_cc: int = engine_cc

    @property
    def color(self) -> str:
        return self._color

    @color.setter
    def color(self, value: str):
        self._color = value
        
    @property
    def engine_cc(self) -> int:
        return self._engine_cc

    @engine_cc.setter
    def engine_cc(self, value: int):
        if value <= 0:
            raise ValueError("Engine CC must be positive.")
        self._engine_cc = value


    def get_wheels_needed(self) -> int:
        return 2

    @property
    def full_description(self) -> str:
        return f"{self.brand} {self.model} {self.engine_cc}cc"

    def __str__(self) -> str:
        base_str = super().__str__()
        return f"{base_str}, Color: {self.color}, Engine: {self.engine_cc}cc"
