from abc import ABC
from uuid import uuid4, UUID
from datetime import datetime
from enum import Enum, auto

class TransactionType(Enum):
    SALE = auto()
    REPAIR = auto()
    VEHICLE_PURCHASE = auto()
    SPARE_PART_PURCHASE = auto()

class Transaction(ABC):
    def __init__(self, transaction_type: TransactionType, amount: float):
        self._id: UUID = uuid4()
        self._timestamp: datetime = datetime.now()
        self._transaction_type: TransactionType = transaction_type
        self._amount: float = amount # Total amount of the transaction

    @property
    def id(self) -> UUID:
        return self._id

    @property
    def timestamp(self) -> datetime:
        return self._timestamp

    @property
    def transaction_type(self) -> TransactionType:
        return self._transaction_type
        
    @property
    def amount(self) -> float:
        return self._amount

    def __str__(self) -> str:
        return (f"Transaction ID: {self._id}, Type: {self._transaction_type.name}, "
                f"Date: {self._timestamp.strftime('%Y-%m-%d %H:%M:%S')}, Amount: {self._amount:.2f}")
