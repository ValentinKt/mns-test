from enum import Enum, auto
from typing import Union
from .transaction import Transaction, TransactionType
from secondhandcar.models.base_vehicle import BaseVehicle
from secondhandcar.models.spare_part import SparePart

class PurchaseItemType(Enum):
    VEHICLE = auto()
    SPARE_PART = auto()

class PurchaseTransaction(Transaction):
    def __init__(self, item: Union[BaseVehicle, SparePart], purchase_price: float, supplier: str = "Unknown"):
        item_type = PurchaseItemType.VEHICLE if isinstance(item, BaseVehicle) else PurchaseItemType.SPARE_PART
        transaction_type = TransactionType.VEHICLE_PURCHASE if item_type == PurchaseItemType.VEHICLE else TransactionType.SPARE_PART_PURCHASE
        
        super().__init__(transaction_type, purchase_price)
        self._item: Union[BaseVehicle, SparePart] = item
        self._supplier: str = supplier
        self._item_type: PurchaseItemType = item_type


    @property
    def item(self) -> Union[BaseVehicle, SparePart]:
        return self._item

    @property
    def supplier(self) -> str:
        return self._supplier
        
    @property
    def item_type(self) -> PurchaseItemType:
        return self._item_type

    def __str__(self) -> str:
        item_desc = f"{self._item.brand} {self._item.model}" if isinstance(self._item, BaseVehicle) else self._item.name
        return (f"{super().__str__()}\n  Item Purchased: {item_desc} (ID: {self._item.id})"
                f"\n  Supplier: {self._supplier}")
