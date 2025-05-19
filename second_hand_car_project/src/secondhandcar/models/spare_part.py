from uuid import uuid4, UUID

class SparePart:
    def __init__(self, name: str, reference: str, purchase_price: float, quantity: int):
        self._id: UUID = uuid4()
        self._name: str = name
        self._reference: str = reference # Manufacturer reference or internal
        self._purchase_price: float = purchase_price
        self._selling_price: float = purchase_price * 1.2 # Example markup
        self._quantity: int = quantity

    @property
    def id(self) -> UUID:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value

    @property
    def reference(self) -> str:
        return self._reference
        
    @reference.setter
    def reference(self, value: str):
        self._reference = value

    @property
    def purchase_price(self) -> float:
        return self._purchase_price

    @purchase_price.setter
    def purchase_price(self, value: float):
        if value < 0:
            raise ValueError("Purchase price cannot be negative.")
        self._purchase_price = value

    @property
    def selling_price(self) -> float:
        return self._selling_price

    @selling_price.setter
    def selling_price(self, value: float):
        if value < 0:
            raise ValueError("Selling price cannot be negative.")
        self._selling_price = value
        
    @property
    def quantity(self) -> int:
        return self._quantity

    @quantity.setter
    def quantity(self, value: int):
        if value < 0:
            raise ValueError("Quantity cannot be negative.")
        self._quantity = value

    def __str__(self) -> str:
        return (f"SparePart(ID: {self._id}, Name: {self._name}, Ref: {self._reference}, "
                f"Qty: {self._quantity}, Price: {self._selling_price:.2f})")

    def __eq__(self, other):
        if not isinstance(other, SparePart):
            return NotImplemented
        return self._id == other._id

    def __hash__(self):
        return hash(self._id)
