from .transaction import Transaction, TransactionType
from secondhandcar.models.base_vehicle import BaseVehicle
from secondhandcar.models.customer import Customer
from typing import Optional

class SaleTransaction(Transaction):
    def __init__(self, vehicle: BaseVehicle, customer: Customer, sale_price: float):
        super().__init__(TransactionType.SALE, sale_price)
        if not isinstance(vehicle, BaseVehicle):
            raise TypeError("Item sold must be a Vehicle.")
        if not isinstance(customer, Customer):
            raise TypeError("Customer must be a Customer object.")
            
        self._vehicle: BaseVehicle = vehicle
        self._customer: Customer = customer

    @property
    def vehicle(self) -> BaseVehicle:
        return self._vehicle

    @property
    def customer(self) -> Customer:
        return self._customer

    def __str__(self) -> str:
        return (f"{super().__str__()}\n  Vehicle: {self._vehicle.full_description} (ID: {self._vehicle.id})"
                f"\n  Customer: {self._customer.full_name} (ID: {self._customer.id})")
