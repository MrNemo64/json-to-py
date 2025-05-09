
from typing import Dict, Type, Union, List, Any, NamedTuple, get_type_hints, Tuple
from dataclasses import is_dataclass, fields
from . import type_information

class _FieldInformation(NamedTuple):
    clazz: Type
    name_in_class: str

def _extract_field_info(clazz: Type) -> Dict[str, _FieldInformation]:
    result = {}

    try:
        type_hints = get_type_hints(clazz, globalns=vars(__import__(clazz.__module__)))
    except Exception as e:
        raise TypeError(f"Failed to resolve type hints for {clazz}: {e}")

    if issubclass(clazz, tuple) and hasattr(clazz, '_fields'):
        for name, typ in type_hints.items():
            result[name] = _FieldInformation(clazz=typ, name_in_class=name)

    elif is_dataclass(clazz):
        for f in fields(clazz):
            json_name = f.metadata.get("json_name", f.name)
            result[json_name] = _FieldInformation(clazz=f.type, name_in_class=f.name)

    else:
        raise TypeError(f"Unsupported class type: {clazz}")

    return result

def _parse_value(value: Any, clazz: Type, field_json_name: str):
    ex = Exception(f"Key {field_json_name} is a {type(value)} but expected a {clazz}")

    if type_information.is_optional(clazz):
        if value is not None:
            value = _parse_value(value, type_information.get_optional_type(clazz), field_json_name)
    elif clazz is str:
        if not isinstance(value, str):
            raise ex
    elif clazz is int:
        if not isinstance(value, int):
            raise ex
    elif clazz is float:
        if not isinstance(value, float):
            raise ex
    elif clazz is bool:
        if not isinstance(value, bool):
            raise ex
    elif type_information.is_list(clazz):
        if not isinstance(value, list):
            raise ex
        clazz = type_information.get_list_type(clazz)
        value = [_parse_value(v, clazz, field_json_name) for v in value]
    return value

def _parse_object(data: Dict, clazz: Type):
    fields = _extract_field_info(clazz)
    values = {}
    for field_json_name, field in fields.items():
        field_value = data.get(field_json_name, None)
        values[field.name_in_class] = _parse_value(field_value, field.clazz, field_json_name)
    return clazz(**values)


def parse_json(data: Union[Dict[str, Any], List[Dict[str, Any]]], clazz: Union[Type, List[Type]]):
    if isinstance(clazz, list):
        if len(clazz) != 1 or not isinstance(clazz[0], type):
            raise Exception()
        if not isinstance(data, list):
            raise Exception()
        return [_parse_object(value, clazz[0]) for value in data]
    
    if not isinstance(clazz, type):
        raise Exception()
    if not isinstance(data, dict):
        raise Exception()
    return _parse_object(data, clazz)