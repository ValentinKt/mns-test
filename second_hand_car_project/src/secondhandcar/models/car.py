from .base_vehicle import BaseVehicle
from .vehicle_type import VehicleType

class Car(BaseVehicle):
    def __init__(self, brand: str, model: str, year: int, price: float,
                 km_driven: int, fuel_type: str, transmission: str, owner_type: str,
                 ecological_bonus_eligible: bool = False):
        super().__init__(brand, model, year, price, VehicleType.CAR)
        self._km_driven: int = km_driven
        self._fuel_type: str = fuel_type
        self._transmission: str = transmission
        self._owner_type: str = owner_type
        self._ecological_bonus_eligible: bool = ecological_bonus_eligible
        
        # Determine eligibility based on fuel type if not explicitly set
        if ecological_bonus_eligible is None: # if not provided, infer
            self._ecological_bonus_eligible = self._fuel_type.upper() in ["CNG", "LPG", "ELECTRIC"]


    @property
    def km_driven(self) -> int:
        return self._km_driven

    @km_driven.setter
    def km_driven(self, value: int):
        if value < 0:
            raise ValueError("Kilometers driven cannot be negative.")
        self._km_driven = value

    @property
    def fuel_type(self) -> str:
        return self._fuel_type

    @fuel_type.setter
    def fuel_type(self, value: str):
        self._fuel_type = value
        # Re-evaluate ecological bonus if fuel type changes
        self._ecological_bonus_eligible = self._fuel_type.upper() in ["CNG", "LPG", "ELECTRIC"]


    @property
    def transmission(self) -> str:
        return self._transmission

    @transmission.setter
    def transmission(self, value: str):
        self._transmission = value

    @property
    def owner_type(self) -> str:
        return self._owner_type

    @owner_type.setter
    def owner_type(self, value: str):
        self._owner_type = value

    @property
    def ecological_bonus_eligible(self) -> bool:
        return self._ecological_bonus_eligible

    @ecological_bonus_eligible.setter
    def ecological_bonus_eligible(self, value: bool):
        self._ecological_bonus_eligible = value

    def get_wheels_needed(self) -> int:
        return 4

    @property
    def full_description(self) -> str:
        return f"{self.brand} {self.model} {self.fuel_type}"

    def __str__(self) -> str:
        base_str = super().__str__()
        return f"{base_str}, KM: {self.km_driven}, Transmission: {self.transmission}, Owner: {self.owner_type}"
