
from typing import Dict, Type, Union, List, Any, NamedTuple, get_type_hints, Tuple
from dataclasses import is_dataclass, fields

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

def _parse_object(data: Dict, clazz: Type):
    fields = _extract_field_info(clazz)

    for field_json_name, field in fields:
        field_value = data.get(field_json_name, None)


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