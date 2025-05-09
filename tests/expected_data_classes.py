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

EXPECTED = {
    "primitive_types": PrimitiveTypes(123, "str", True, None, 456, 1.2),
    "list_of_primitive_types": [PrimitiveTypes(123, "str", True, None, 456, 1.2), PrimitiveTypes(123123, "strstr", False, None, 456456, 12.3)],
    "lists_with_lists": Matrix([[1, 2, 3],[4, 5, 6],[7, 8, 9]])
}