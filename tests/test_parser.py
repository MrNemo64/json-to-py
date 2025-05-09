import unittest
import os
import json
from json_to_py.parser import parse_json

import tests.expected_named_tuples as expected_named_tuples
import tests.expected_data_classes as expected_data_classes

def generate_expected(module):
    PrimitiveTypes = module.PrimitiveTypes
    Matrix = module.Matrix
    Address = module.Address
    Person = module.Person

    return {
        "primitive_types": PrimitiveTypes(123, "str", True, None, 456, 1.2),
        "list_of_primitive_types": [
            PrimitiveTypes(123, "str", True, None, 456, 1.2),
            PrimitiveTypes(123123, "strstr", False, None, 456456, 12.3)
        ],
        "lists_with_lists": Matrix([[1, 2, 3], [4, 5, 6], [7, 8, 9]]),
        "nested_data_class": Person(
            name="Alice",
            age=30,
            address=Address(
                street="123 Main St",
                city="Wonderland",
                postal_code="12345"
            )
        ),
    }


class TestTypeHelpers(unittest.TestCase):
    
    def setUp(self):
        """Setup function to load all JSON files into memory for the tests."""
        self.json_data = {}
        jsons_dir = os.path.join(os.path.dirname(__file__), 'jsons')
        
        for filename in os.listdir(jsons_dir):
            if filename.endswith('.json'):
                with open(os.path.join(jsons_dir, filename), 'r') as f:
                    self.json_data[filename.replace('.json', '')] = json.load(f)

    def test_named_tuple_all_ok(self):
        """Tests that the JSON files under /jsons are correctly parsed into NamedTuples."""
        EXPECTED_NAMED_TUPLES = generate_expected(expected_named_tuples)
        for json_name, data in self.json_data.items():
            with self.subTest(json=json_name):
                expected_value = EXPECTED_NAMED_TUPLES.get(json_name)
                if isinstance(expected_value, list):
                    parsed_value = parse_json(data, [type(expected_value[0])])
                else:
                    parsed_value = parse_json(data, type(expected_value))
                self.assertEqual(parsed_value, expected_value)

    def test_data_class_all_ok(self):
        """Tests that the JSON files under /jsons are correctly parsed into DataClasses."""
        EXPECTED_DATA_CLASSES = generate_expected(expected_data_classes)
        for json_name, data in self.json_data.items():
            with self.subTest(json=json_name):
                expected_value = EXPECTED_DATA_CLASSES.get(json_name)
                if isinstance(expected_value, list):
                    parsed_value = parse_json(data, [type(expected_value[0])])
                else:
                    parsed_value = parse_json(data, type(expected_value))
                self.assertEqual(parsed_value, expected_value)

if __name__ == "__main__":
    unittest.main()
