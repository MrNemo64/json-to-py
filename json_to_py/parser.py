
from typing import Dict, Type, Union, List, Any, NamedTuple, get_type_hints, Tuple
from dataclasses import is_dataclass, fields
from . import type_information

def _parse_value(value: Any, clazz: Type, field_json_name: str):
    ex = Exception(f"Key {field_json_name} is a {type(value)} but expected a {clazz}")

    if clazz is Any:
        return value
    
    elif type_information.is_optional(clazz):
        if value is not None:
            value = _parse_value(value, type_information.get_optional_type(clazz), field_json_name)
        return value

    elif clazz is str:
        if not isinstance(value, str):
            raise ex
        return value

    elif clazz is int:
        if not isinstance(value, int):
            raise ex
        return value

    elif clazz is float:
        if not isinstance(value, float):
            raise ex
        return value

    elif clazz is bool:
        if not isinstance(value, bool):
            raise ex
        return value

    elif type_information.is_list(clazz):
        if not isinstance(value, list):
            raise ex
        clazz = type_information.get_list_type(clazz)
        return [_parse_value(v, clazz, field_json_name) for v in value]

    elif type_information.is_dict(clazz):
        if not isinstance(value, dict):
            raise ex
        key_clazz, value_clazz = type_information.get_dict_types(clazz)
        if not key_clazz is str:
            raise Exception(f"Dict keys must be strings not {key_clazz}")
        return {k: _parse_value(v, value_clazz) for k, v in value}

    elif type_information.is_set(clazz):
        if not isinstance(value, list):
            raise ex
        clazz = type_information.get_set_type(clazz)
        return {_parse_value(v, clazz, field_json_name) for v in value}

    elif type_information.is_tuple(clazz):
        if not isinstance(value, list):
            raise ex
        classes = type_information.get_tuple_types(clazz)
        if len(classes) != len(value):
            raise Exception(f"Expected tuple to have {len(classes)} but has {len(value)}")
        return tuple(_parse_value(value[i], classes[i], field_json_name) for i in range(len(value)))
    
    elif type_information.is_union(clazz):
        ex_msg = []
        classes = type_information.get_union_types(clazz)
        found = False
        for c in classes:
            try:
                value = _parse_value(value, c, field_json_name)
                return value
            except Exception as e:
                ex_msg.append(e)
        raise Exception(f"Key {field_json_name} is an union but no option matches it: " + ",".join(ex_msg))
    
    elif type_information.is_literal(clazz):
        literal_values = type_information.get_literal_values(clazz)
        if value not in literal_values:
            raise Exception(f"Key {field_json_name} has value {value}, but expected one of {literal_values}")
        return value

    elif type_information.is_supported_class(clazz):
        return _parse_object(value, clazz)

    raise Exception(f"Cannot parse {clazz}")

def _parse_object(data: Dict, clazz: Type):
    fields = type_information.extract_field_info(clazz)
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