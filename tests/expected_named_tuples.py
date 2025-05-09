import sys
from typing import Dict, NamedTuple, Optional, List, Set, Union

if sys.version_info < (3, 8):
    from typing_extensions import Literal
else:
    from typing import Literal

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
    products: List[Product]

class OrderSet(NamedTuple):
    id: int
    products: Set[Product]

class OrderDict(NamedTuple):
    id: int
    products: Dict[str, Product]

class Status(NamedTuple):
    status: Literal["active", "inactive"]