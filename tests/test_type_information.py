from dataclasses import dataclass, field
from typing import Optional, List, Dict, Set, Tuple
from json_to_py.type_information import *
import unittest

class TestTypeHelpers(unittest.TestCase):
    def test_optional_type(self):
        self.assertTrue(is_optional(Optional[int]))
        self.assertIs(get_optional_type(Optional[int]), int)
        self.assertFalse(is_optional(int))
        with self.assertRaises(TypeError):
            get_optional_type(int)

    def test_list_type(self):
        self.assertTrue(is_list(List[str]))
        self.assertIs(get_list_type(List[str]), str)
        self.assertFalse(is_list(str))
        with self.assertRaises(TypeError):
            get_list_type(str)

    def test_dict_type(self):
        self.assertTrue(is_dict(Dict[str, int]))
        self.assertEqual(get_dict_types(Dict[str, int]), (str, int))
        self.assertFalse(is_dict(int))
        with self.assertRaises(TypeError):
            get_dict_types(int)

    def test_set_type(self):
        self.assertTrue(is_set(Set[float]))
        self.assertIs(get_set_type(Set[float]), float)
        self.assertFalse(is_set(float))
        with self.assertRaises(TypeError):
            get_set_type(float)

    def test_tuple_type(self):
        self.assertTrue(is_tuple(Tuple[int, str]))
        self.assertEqual(get_tuple_types(Tuple[int, str]), (int, str))
        self.assertFalse(is_tuple(int))
        with self.assertRaises(TypeError):
            get_tuple_types(int)

    def test_union_type(self):
        self.assertTrue(is_union(Union[int, str]))
        self.assertEqual(get_union_types(Union[int, str]), (int, str))
        self.assertFalse(is_union(int))
        with self.assertRaises(TypeError):
            get_union_types(int)

    def test_literal(self):
        self.assertTrue(is_literal(Literal[1, 2, 3]))
        self.assertEqual(get_literal_values(Literal[1, 2, 3]), (1, 2, 3))
        self.assertFalse(is_literal(int))
        
        with self.assertRaises(TypeError):
            get_literal_values(int)

    def test_namedtuple(self):
        class Point(NamedTuple):
            x: int
            y: int
        field_info = extract_field_info(Point)
        self.assertIn('x', field_info)
        self.assertIn('y', field_info)
        self.assertEqual(field_info['x'].clazz, int)
        self.assertEqual(field_info['y'].clazz, int)

    def test_dataclass(self):
        @dataclass
        class Point:
            x: int
            y: int
            z: Optional[int] = field(default=None, metadata={"json-to-py": {"name": "altitude"}})

        field_info = extract_field_info(Point)
        self.assertIn('x', field_info)
        self.assertIn('y', field_info)
        self.assertIn('altitude', field_info)
        self.assertEqual(field_info['x'].clazz, int)
        self.assertEqual(field_info['y'].clazz, int)
        self.assertEqual(field_info['altitude'].clazz, Optional[int])
        self.assertEqual(field_info['altitude'].name_in_class, 'z')

    def test_extract_field_info_invalid(self):
        self.assertRaises(TypeError, extract_field_info, int)

    def test_unsupported_dataclass_metadata(self):
        @dataclass
        class BadMeta:
            a: int = field(metadata={"json-to-py": "not a dict"})
        with self.assertRaises(InvalidJsonToPyMedatada):
            extract_field_info(BadMeta)

if __name__ == "__main__":
    unittest.main()
