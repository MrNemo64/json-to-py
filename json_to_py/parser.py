
from typing import Dict, Type, Union, List, Any
from . import type_information

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

class UnexpectedTypeException(Exception):
    def __init__(self, actual_value: Any, expected_type: Type, json_path: List[Union[str, int]]):
        full_path = _print_json_path(json_path)
        super().__init__(f"Key {full_path} is a {type(actual_value)} but expected a {expected_type}")
        self.actual_value = actual_value
        self.expected_type = expected_type
        self.json_path = json_path
        self.full_path = full_path

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
        if not isinstance(value, int):
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
            raise Exception(f"Dict keys must be strings not {key_clazz}")
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
            raise Exception(f"Expected tuple to have {len(classes)} but has {len(value)}")
        return tuple(_parse_value(value[i], classes[i], json_path) for i in range(len(value)))
    
    elif type_information.is_union(clazz):
        ex_msg = []
        classes = type_information.get_union_types(clazz)
        found = False
        for c in classes:
            try:
                value = _parse_value(value, c, json_path)
                return value
            except Exception as e:
                ex_msg.append(e)
        raise Exception(f"Key {json_path} is an union but no option matches it: " + ",".join(ex_msg))
    
    elif type_information.is_literal(clazz):
        literal_values = type_information.get_literal_values(clazz)
        if value not in literal_values:
            raise Exception(f"Key {json_path} has value {value}, but expected one of {literal_values}")
        return value

    elif type_information.is_supported_class(clazz):
        return _parse_object(value, clazz, json_path)

    raise Exception(f"Cannot parse {clazz} at json path {'.'.join(json_path)}")

def _parse_object(data: Dict, clazz: Type, json_path: List[str]):
    fields = type_information.extract_field_info(clazz)
    values = {}
    for field_json_name, field in fields.items():
        field_value = data.get(field_json_name, None)
        values[field.name_in_class] = _parse_value(field_value, field.clazz, json_path + [field_json_name])
    return clazz(**values)

def parse_json(data: Any, clazz: Type):
    return _parse_value(data, clazz, [])