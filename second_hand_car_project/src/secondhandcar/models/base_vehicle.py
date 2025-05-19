from abc import ABC, abstractmethod
from uuid import uuid4, UUID
from datetime import date

from secondhandcar.models.vehicle_type import VehicleType

class BaseVehicle(ABC):
    def __init__(self, brand: str, model: str, year: int, price: float, vehicle_type: 'VehicleType'):
        self._id: UUID = uuid4()
        self._brand: str = brand
        self._model: str = model
        self._year: int = year
        self._price: float = price
        self._vehicle_type: 'VehicleType' = vehicle_type
        self._is_sold: bool = False
        self._is_available: bool = True # Available for sale or repair

    @property
    def id(self) -> UUID:
        return self._id

    @id.setter
    def id(self, value: UUID): # Allow setting ID for loading from persistence
        if isinstance(value, str):
            self._id = UUID(value)
        elif isinstance(value, UUID):
            self._id = value
        else:
            raise TypeError("ID must be a UUID object or a string representation of a UUID.")


    @property
    def brand(self) -> str:
        return self._brand

    @brand.setter
    def brand(self, value: str):
        self._brand = value

    @property
    def model(self) -> str:
        return self._model

    @model.setter
    def model(self, value: str):
        self._model = value

    @property
    def year(self) -> int:
        return self._year

    @year.setter
    def year(self, value: int):
        self._year = value

    @property
    def price(self) -> float:
        return self._price

    @price.setter
    def price(self, value: float):
        if value < 0:
            raise ValueError("Price cannot be negative.")
        self._price = value

    @property
    def vehicle_type(self) -> 'VehicleType':
        return self._vehicle_type

    @property
    def is_sold(self) -> bool:
        return self._is_sold

    @is_sold.setter
    def is_sold(self, value: bool):
        self._is_sold = value
        if value: # if sold, it's not available
            self._is_available = False

    @property
    def is_available(self) -> bool:
        return self._is_available

    @is_available.setter
    def is_available(self, value: bool):
        self._is_available = value
        if not value and not self._is_sold: # if made unavailable but not sold (e.g. in repair)
            pass
        elif value: # if made available
            self._is_sold = False


    @abstractmethod
    def get_wheels_needed(self) -> int:
        pass

    @property
    @abstractmethod
    def full_description(self) -> str:
        pass

    def __str__(self) -> str:
        return f"{self.vehicle_type.name}: {self.full_description}, Year: {self.year}, Price: {self.price:.2f}"

    def __eq__(self, other):
        if not isinstance(other, BaseVehicle):
            return NotImplemented
        return self._id == other._id

    def __hash__(self):
        return hash(self._id)
