from typing import Optional, List, Dict, Set, Tuple
from json_to_py.type_information import *
import unittest

class TestTypeHelpers(unittest.TestCase):
    def test_types(self):
        self.assertTrue(is_optional(Optional[int]))
        self.assertIs(get_optional_type(Optional[int]), int)

        self.assertTrue(is_list(List[str]))
        self.assertIs(get_list_type(List[str]), str)

        self.assertTrue(is_dict(Dict[str, int]))
        self.assertEqual(get_dict_types(Dict[str, int]), (str, int))

        self.assertTrue(is_set(Set[float]))
        self.assertIs(get_set_type(Set[float]), float)

        self.assertTrue(is_tuple(Tuple[int, str]))
        self.assertEqual(get_tuple_types(Tuple[int, str]), (int, str))

if __name__ == "__main__":
    unittest.main()
