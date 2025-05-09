from typing import Optional, List
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