from typing import NamedTuple, Optional

class PrimitiveTypes(NamedTuple):
    integer: int
    string: str
    boolean: bool
    optional_null: Optional[int]
    optional_int: Optional[int]
    float: float

EXPECTED = {
    "primitive_types": PrimitiveTypes(123, "str", True, None, 456, 1.2),
        "list_of_primitive_types": [PrimitiveTypes(123, "str", True, None, 456, 1.2), PrimitiveTypes(123123, "strstr", False, None, 456456, 12.3)]
}