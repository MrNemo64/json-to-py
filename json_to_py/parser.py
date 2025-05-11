
import sys
from typing import Dict, Optional, Tuple, Type, TypeVar, Union, List, Any
from . import type_information

if sys.version_info < (3, 8):
    from typing_extensions import Literal
else:
    from typing import Literal

def _print_json_path(items: List[Union[str, int]]) -> str:
    result = []
    for item in items:
        if isinstance(item, str):
            if result:
                result.append(".")
            result.append(item)
        else:
            result.append("[" + str(item) + "]")
    return ''.join(result)

class JsonParsingException(Exception):
    """
    Base class for exceptions raised during JSON parsing.

    Attributes:
        msg (str): A message describing the error.
        json_path (List[Union[str, int]]): A list representing the path to the location in the JSON where the error occurred.
        full_path (str): A string representation of the JSON path for display purposes.
    """
    def __init__(self, msg: str, json_path: List[Union[str, int]], full_path: Optional[str] = None):
        full_path = _print_json_path(json_path) if full_path is None else full_path
        super().__init__(msg)
        self.json_path = json_path
        self.full_path = full_path

class UnexpectedTypeException(JsonParsingException):
    """
    Raised when the type of a JSON value does not match the expected type.

    Attributes:
        actual_value (Any): The actual value encountered in the JSON.
        expected_type (Type): The expected Python type.
    """
    def __init__(self, actual_value: Any, expected_type: Type, json_path: List[Union[str, int]], full_path: Optional[str] = None, msg: Optional[str] = None):
        full_path = _print_json_path(json_path) if full_path is None else full_path
        msg = f"Key {full_path} is a {type(actual_value)} but expected a {expected_type}" if msg is None else msg
        super().__init__(msg, json_path, full_path)
        self.actual_value = actual_value
        self.expected_type = expected_type

class NoUnionVariantException(UnexpectedTypeException):
    """
    Raised when none of the Union type variants match the JSON value.

    Attributes:
        union_variants (Tuple[Type]): The expected Union type variants.
        exceptions (List[JsonParsingException]): Exceptions raised while trying each Union variant.
    """
    def __init__(self, actual_value: Any, variants: Tuple[Type], exceptions: List[JsonParsingException], json_path: List[Union[str, int]], full_path: Optional[str] = None):
        full_path = _print_json_path(json_path) if full_path is None else full_path
        super().__init__(actual_value, Union, json_path, full_path, f"None of the union variants at {full_path} matched the value {actual_value}: {', '.join(map(str, exceptions))}")
        self.union_variants = variants
        self.exceptions = exceptions

class NonStringKeyException(UnexpectedTypeException):
    """
    Raised when a dictionary key is not a string, which is invalid in JSON.

    Attributes:
        key_clazz (Type): The type of the dictionary key encountered.
    """
    def __init__(self, actual_value: Any, key_clazz: Type, json_path: List[Union[str, int]], full_path: Optional[str] = None):
        full_path = _print_json_path(json_path) if full_path is None else full_path
        super().__init__(actual_value, str, json_path, full_path, f"Dict keys must be strings but at {full_path} the keys are {key_clazz}")
        self.key_clazz = key_clazz

class NoLiteralVariantException(UnexpectedTypeException):
    """
    Raised when a JSON value does not match any expected Literal values.

    Attributes:
        varian_values (Tuple[Any]): Allowed literal values.
    """
    def __init__(self, actual_value: Any, expected_values: Tuple[Any], json_path: List[Union[str, int]], full_path: Optional[str] = None):
        full_path = _print_json_path(json_path) if full_path is None else full_path
        super().__init__(actual_value, Literal, json_path, full_path, f"No literal variant of the list [{', '.join(map(str, expected_values))}] matched the value {actual_value} at {full_path}")
        self.varian_values = expected_values

class InvalidTupleSizeException(UnexpectedTypeException):
    """
    Raised when a JSON list does not match the expected length for a Tuple.

    Attributes:
        tuple_size (int): The expected number of elements in the tuple.
    """
    def __init__(self, actual_value: Any, tuple_size: int, json_path: List[Union[str, int]], full_path: Optional[str] = None):
        full_path = _print_json_path(json_path) if full_path is None else full_path
        super().__init__(actual_value, Tuple, json_path, full_path, f"Expected json list {actual_value} at {full_path} to have {tuple_size} elements but has {len(actual_value)}")
        self.tuple_size = tuple_size

class CanNotParseTypeException(JsonParsingException):
    """
    Raised when a value cannot be parsed into the expected class type.

    Attributes:
        actual_value (Any): The JSON value that could not be parsed.
        clazz (Type): The class type that was expected.
    """
    def __init__(self, actual_value: Any, clazz: Type, json_path: List[Union[str, int]], full_path: Optional[str] = None):
        full_path = _print_json_path(json_path) if full_path is None else full_path
        super().__init__(f"Cannot parse {clazz} at {full_path}", json_path, full_path)
        self.actual_value = actual_value
        self.clazz = clazz

def _parse_value(value: Any, clazz: Type, json_path: List[str]):
    if clazz is Any:
        return value
    
    elif type_information.is_optional(clazz):
        if value is not None:
            value = _parse_value(value, type_information.get_optional_type(clazz), json_path)
        return value

    elif clazz is str:
        if not isinstance(value, str):
            raise UnexpectedTypeException(value, str, json_path)
        return value

    elif clazz is int:
        if not isinstance(value, int) or value is True or value is False:
            raise UnexpectedTypeException(value, int, json_path)
        return value

    elif clazz is float:
        if not isinstance(value, float):
            raise UnexpectedTypeException(value, float, json_path)
        return value

    elif clazz is bool:
        if not isinstance(value, bool):
            raise UnexpectedTypeException(value, bool, json_path)
        return value

    elif type_information.is_list(clazz):
        if not isinstance(value, list):
            raise UnexpectedTypeException(value, list, json_path)
        clazz = type_information.get_list_type(clazz)
        return [_parse_value(v, clazz, json_path + [i]) for i, v in enumerate(value)]

    elif type_information.is_dict(clazz):
        if not isinstance(value, dict):
            raise UnexpectedTypeException(value, dict, json_path)
        key_clazz, value_clazz = type_information.get_dict_types(clazz)
        if not key_clazz is str:
            raise NonStringKeyException(value, key_clazz, json_path)
        return {k: _parse_value(v, value_clazz, json_path + [k]) for k, v in value.items()}

    elif type_information.is_set(clazz):
        if not isinstance(value, list):
            raise UnexpectedTypeException(value, list, json_path)
        clazz = type_information.get_set_type(clazz)
        return {_parse_value(v, clazz, json_path) for v in value}

    elif type_information.is_tuple(clazz):
        if not isinstance(value, list):
            raise UnexpectedTypeException(value, list, json_path)
        classes = type_information.get_tuple_types(clazz)
        if len(classes) != len(value):
            raise InvalidTupleSizeException(value, len(classes), json_path)
        return tuple(_parse_value(value[i], classes[i], json_path) for i in range(len(value)))
    
    elif type_information.is_union(clazz):
        ex_msg = []
        classes = type_information.get_union_types(clazz)
        for c in classes:
            try:
                value = _parse_value(value, c, json_path)
                return value
            except Exception as e:
                ex_msg.append(e)
        raise NoUnionVariantException(value, classes, ex_msg, json_path)
    
    elif type_information.is_literal(clazz):
        literal_values = type_information.get_literal_values(clazz)
        if value not in literal_values:
            raise NoLiteralVariantException(value, literal_values, json_path)
        return value

    elif type_information.is_supported_class(clazz):
        return _parse_object(value, clazz, json_path)

    raise CanNotParseTypeException(value, clazz, json_path)

def _parse_object(data: Dict, clazz: Type, json_path: List[str]):
    fields = type_information.extract_field_info(clazz)
    values = {}
    for field_json_name, field in fields.items():
        field_value = data.get(field_json_name, None)
        values[field.name_in_class] = _parse_value(field_value, field.clazz, json_path + [field_json_name])
    return clazz(**values)

JSONType = Union[None, bool, int, float, str, List["JSONType"], Dict[str, "JSONType"]]
T = TypeVar('T')
def parse_json(data: JSONType, clazz: Type[T]) -> T:
    """
    Parses JSON data into a specified Python class structure.

    Args:
        data (JSONType): The input JSON data as a primitive or nested structure.
        clazz (Type[T]): The target Python type (including custom classes) to parse the data into.

    Returns:
        T: An instance of the target Python type populated with the parsed data.

    Raises:
        UnexpectedTypeException: If a value does not match the expected type.
        NoUnionVariantException: If none of the Union type variants match the value.
        NonStringKeyException: If a dictionary key is not a string.
        NoLiteralVariantException: If a value does not match any of the allowed Literal values.
        InvaludTupleSizeException: If a list does not match the expected size of a Tuple.
        CanNotParseTypeException: If a value cannot be parsed into the expected class type.
        InvalidJsonToPyMedatada: If the field of a data class has invalid metadata.
    """
    return _parse_value(data, clazz, [])