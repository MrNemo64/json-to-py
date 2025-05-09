from typing import NamedTuple, Optional, List

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