import types
from typing import (
    Type, Tuple, Union, Any, List, Dict, Set, get_args, get_origin
)
import sys

def is_optional(clazz: Type) -> bool:
    origin = get_origin(clazz)
    args = get_args(clazz)

    if origin is Union:
        return type(None) in args
    elif sys.version_info >= (3, 10):
        return clazz.__class__ is types.UnionType and type(None) in clazz.__args__
    return False

def get_optional_type(clazz: Type) -> Type:
    if not is_optional(clazz):
        raise TypeError("Type is not Optional")

    args = get_args(clazz)
    return next(arg for arg in args if arg is not type(None))


def is_list(clazz: Type) -> bool:
    return get_origin(clazz) in (list, List)

def get_list_type(clazz: Type) -> Type:
    if not is_list(clazz):
        raise TypeError("Type is not List")

    args = get_args(clazz)
    return args[0] if args else Any


def is_dict(clazz: Type) -> bool:
    return get_origin(clazz) in (dict, Dict)

def get_dict_types(clazz: Type) -> Tuple[Type, Type]:
    if not is_dict(clazz):
        raise TypeError("Type is not Dict")

    args = get_args(clazz)
    return args if args else (Any, Any)


def is_set(clazz: Type) -> bool:
    return get_origin(clazz) in (set, Set)

def get_set_type(clazz: Type) -> Type:
    if not is_set(clazz):
        raise TypeError("Type is not Set")

    args = get_args(clazz)
    return args[0] if args else Any


def is_tuple(clazz: Type) -> bool:
    return get_origin(clazz) in (tuple, Tuple)

def get_tuple_types(clazz: Type) -> Tuple[Type, ...]:
    if not is_tuple(clazz):
        raise TypeError("Type is not Tuple")

    return get_args(clazz) or (Any,)
