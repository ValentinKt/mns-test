from typing import List, Optional
from .transaction import Transaction, TransactionType
from secondhandcar.models.base_vehicle import BaseVehicle
from secondhandcar.models.customer import Customer
from secondhandcar.models.spare_part import SparePart

class RepairTransaction(Transaction):
    def __init__(self, vehicle: BaseVehicle, customer: Customer, description: str, cost: float, 
                 spare_parts_used: Optional[List[SparePart]] = None):
        super().__init__(TransactionType.REPAIR, cost)
        if not isinstance(vehicle, BaseVehicle):
            raise TypeError("Repaired item must be a Vehicle.")
        if not isinstance(customer, Customer):
            raise TypeError("Customer must be a Customer object.")

        self._vehicle: BaseVehicle = vehicle
        self._customer: Customer = customer
        self._description: str = description
        self._spare_parts_used: List[SparePart] = spare_parts_used if spare_parts_used else []

    @property
    def vehicle(self) -> BaseVehicle:
        return self._vehicle

    @property
    def customer(self) -> Customer:
        return self._customer

    @property
    def description(self) -> str:
        return self._description

    @property
    def spare_parts_used(self) -> List[SparePart]:
        return self._spare_parts_used

    def add_spare_part(self, part: SparePart):
        if not isinstance(part, SparePart):
            raise TypeError("Can only add SparePart objects.")
        self._spare_parts_used.append(part)
        # Potentially adjust total cost here or handle it in a service
        # self._amount += part.selling_price 

    def __str__(self) -> str:
        parts_str = ", ".join([part.name for part in self._spare_parts_used]) if self._spare_parts_used else "None"
        return (f"{super().__str__()}\n  Vehicle: {self._vehicle.full_description} (ID: {self._vehicle.id})"
                f"\n  Customer: {self._customer.full_name} (ID: {self._customer.id})"
                f"\n  Description: {self._description}\n  Spare Parts Used: {parts_str}")
