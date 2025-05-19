from uuid import uuid4, UUID

class Customer:
    def __init__(self, last_name: str, email: str, first_name: str = None):
        self._id: UUID = uuid4()
        self._first_name: str = first_name
        self._last_name: str = last_name
        self._email: str = email
        self._phone: str = None
        self._address: str = None

    @property
    def id(self) -> UUID:
        return self._id

    @property
    def first_name(self) -> str:
        return self._first_name

    @first_name.setter
    def first_name(self, value: str):
        self._first_name = value

    @property
    def last_name(self) -> str:
        return self._last_name

    @last_name.setter
    def last_name(self, value: str):
        self._last_name = value

    @property
    def email(self) -> str:
        return self._email

    @email.setter
    def email(self, value: str):
        # Basic email validation could be added here
        self._email = value

    @property
    def phone(self) -> str:
        return self._phone

    @phone.setter
    def phone(self, value: str):
        self._phone = value

    @property
    def address(self) -> str:
        return self._address

    @address.setter
    def address(self, value: str):
        self._address = value

    @property
    def full_name(self) -> str:
        if self._first_name:
            return f"{self._first_name} {self._last_name}"
        return self._last_name

    def __str__(self) -> str:
        return f"Customer(ID: {self._id}, Name: {self.full_name}, Email: {self._email})"

    def __eq__(self, other):
        if not isinstance(other, Customer):
            return NotImplemented
        return self._id == other._id

    def __hash__(self):
        return hash(self._id)
