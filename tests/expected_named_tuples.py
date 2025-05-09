from typing import Literal, NamedTuple, Optional, List, Union

class PrimitiveTypes(NamedTuple):
    integer: int
    string: str
    boolean: bool
    optional_null: Optional[int]
    optional_int: Optional[int]
    float: float

class Matrix(NamedTuple):
    matrix: List[List[int]]

class Address(NamedTuple):
    street: str
    city: str
    postal_code: str

class Person(NamedTuple):
    name: str
    age: int
    address: Address


class Item(NamedTuple):
    id: int
    value: Union[str, float]

class Product(NamedTuple):
    name: str
    price: float

class OrderList(NamedTuple):
    id: int
    products: list[Product]

class OrderSet(NamedTuple):
    id: int
    products: set[Product]

class Status(NamedTuple):
    status: Literal["active", "inactive"]