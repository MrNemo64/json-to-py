import types
import sys

# Conditional import based on Python version
if sys.version_info < (3, 8):
    from typing_extensions import get_args, get_origin, Literal
else:
    from typing import get_args, get_origin, Literal

from typing import Type, Tuple, Union, Any, List, Dict, Set


def is_optional(clazz: Type) -> bool:
    """
    Checks if the given type is Optional (i.e., a Union of a type and None).

    Args:
        clazz (Type): The type to check.

    Returns:
        bool: True if the type is Optional, False otherwise.
    """
    origin = get_origin(clazz)
    args = get_args(clazz)

    if origin is Union:
        return type(None) in args
    elif sys.version_info >= (3, 10):
        return clazz.__class__ is types.UnionType and type(None) in clazz.__args__
    return False


def get_optional_type(clazz: Type) -> Type:
    """
    Retrieves the type inside an Optional type.

    Args:
        clazz (Type): The type to extract the inner type from.

    Returns:
        Type: The type inside the Optional (i.e., the non-None type).

    Raises:
        TypeError: If the given type is not Optional.
    """
    if not is_optional(clazz):
        raise TypeError("Type is not Optional")

    args = get_args(clazz)
    return next(arg for arg in args if arg is not type(None))


def is_list(clazz: Type) -> bool:
    """
    Checks if the given type is a List.

    Args:
        clazz (Type): The type to check.

    Returns:
        bool: True if the type is a List, False otherwise.
    """
    return get_origin(clazz) in (list, List)


def get_list_type(clazz: Type) -> Type:
    """
    Retrieves the type of elements inside a List.

    Args:
        clazz (Type): The List type to extract the element type from.

    Returns:
        Type: The type of elements inside the List.

    Raises:
        TypeError: If the given type is not a List.
    """
    if not is_list(clazz):
        raise TypeError("Type is not List")

    args = get_args(clazz)
    return args[0] if args else Any


def is_dict(clazz: Type) -> bool:
    """
    Checks if the given type is a Dict.

    Args:
        clazz (Type): The type to check.

    Returns:
        bool: True if the type is a Dict, False otherwise.
    """
    return get_origin(clazz) in (dict, Dict)


def get_dict_types(clazz: Type) -> Tuple[Type, Type]:
    """
    Retrieves the key and value types inside a Dict.

    Args:
        clazz (Type): The Dict type to extract key and value types from.

    Returns:
        Tuple[Type, Type]: A tuple containing the key and value types.

    Raises:
        TypeError: If the given type is not a Dict.
    """
    if not is_dict(clazz):
        raise TypeError("Type is not Dict")

    args = get_args(clazz)
    return args if args else (Any, Any)


def is_set(clazz: Type) -> bool:
    """
    Checks if the given type is a Set.

    Args:
        clazz (Type): The type to check.

    Returns:
        bool: True if the type is a Set, False otherwise.
    """
    return get_origin(clazz) in (set, Set)


def get_set_type(clazz: Type) -> Type:
    """
    Retrieves the type of elements inside a Set.

    Args:
        clazz (Type): The Set type to extract the element type from.

    Returns:
        Type: The type of elements inside the Set.

    Raises:
        TypeError: If the given type is not a Set.
    """
    if not is_set(clazz):
        raise TypeError("Type is not Set")

    args = get_args(clazz)
    return args[0] if args else Any


def is_tuple(clazz: Type) -> bool:
    """
    Checks if the given type is a Tuple.

    Args:
        clazz (Type): The type to check.

    Returns:
        bool: True if the type is a Tuple, False otherwise.
    """
    return get_origin(clazz) in (tuple, Tuple)


def get_tuple_types(clazz: Type) -> Tuple[Type, ...]:
    """
    Retrieves the types of elements inside a Tuple.

    Args:
        clazz (Type): The Tuple type to extract element types from.

    Returns:
        Tuple[Type, ...]: A tuple of types representing the elements inside the Tuple.

    Raises:
        TypeError: If the given type is not a Tuple.
    """
    if not is_tuple(clazz):
        raise TypeError("Type is not Tuple")

    return get_args(clazz) or (Any,)


def is_union(clazz: Type) -> bool:
    """
    Checks if the given type is a Union.

    Args:
        clazz (Type): The type to check.

    Returns:
        bool: True if the type is a Union, False otherwise.
    """
    origin = get_origin(clazz)
    if origin is Union:
        return True
    if sys.version_info >= (3, 10):
        return clazz.__class__ is types.UnionType
    return False


def get_union_types(clazz: Type) -> Tuple[Type, ...]:
    """
    Retrieves the individual types inside a Union.

    Args:
        clazz (Type): The Union type.

    Returns:
        Tuple[Type, ...]: A tuple of types in the Union.

    Raises:
        TypeError: If the given type is not a Union.
    """
    if not is_union(clazz):
        raise TypeError("Type is not Union")

    return get_args(clazz) or (Any,)

def is_literal(clazz: Type) -> bool:
    """
    Checks if the given type is a Literal.

    Args:
        clazz (Type): The type to check.

    Returns:
        bool: True if the type is a Literal, False otherwise.
    """
    return get_origin(clazz) is Literal


def get_literal_values(clazz: Type) -> Tuple[Any, ...]:
    """
    Retrieves the possible values from a Literal type.

    Args:
        clazz (Type): The Literal type to extract values from.

    Returns:
        Tuple[Any, ...]: A tuple of all acceptable literal values.

    Raises:
        TypeError: If the given type is not a Literal.
    """
    if not is_literal(clazz):
        raise TypeError("Type is not a Literal")
    return get_args(clazz)
