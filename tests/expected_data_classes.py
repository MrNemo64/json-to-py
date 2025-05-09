from typing import Literal, Optional, List, Union
from dataclasses import dataclass

@dataclass
class PrimitiveTypes():
    integer: int
    string: str
    boolean: bool
    optional_null: Optional[int]
    optional_int: Optional[int]
    float: float

@dataclass
class Matrix():
    matrix: List[List[int]]

@dataclass
class Address:
    street: str
    city: str
    postal_code: str

@dataclass
class Person:
    name: str
    age: int
    address: Address

@dataclass
class Item:
    id: int
    value: Union[str, float]

@dataclass(frozen=True)
class Product:
    name: str
    price: float

@dataclass
class OrderList:
    id: int
    products: list[Product]

@dataclass
class OrderSet:
    id: int
    products: set[Product]

@dataclass
class OrderDict:
    id: int
    products: dict[str, Product]

@dataclass
class Status:
    status: Literal["active", "inactive"]