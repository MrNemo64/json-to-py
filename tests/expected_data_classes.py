import sys
from typing import Dict, Optional, List, Set, Union
from dataclasses import dataclass

if sys.version_info < (3, 8):
    from typing_extensions import Literal
else:
    from typing import Literal

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
    products: List[Product]

@dataclass
class OrderSet:
    id: int
    products: Set[Product]

@dataclass
class OrderDict:
    id: int
    products: Dict[str, Product]

@dataclass
class Status:
    status: Literal["active", "inactive"]