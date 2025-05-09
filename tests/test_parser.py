import unittest
import os
import json
from json_to_py.parser import parse_json
from json_to_py import type_information

from tests.expected_named_tuples import EXPECTED as EXPECTED_NAMED_TUPLES
from tests.expected_data_classes import EXPECTED as EXPECTED_DATA_CLASSES

class TestTypeHelpers(unittest.TestCase):
    
    def setUp(self):
        """Setup function to load all JSON files into memory for the tests."""
        self.json_data = {}
        jsons_dir = os.path.join(os.path.dirname(__file__), 'jsons')
        
        for filename in os.listdir(jsons_dir):
            if filename.endswith('.json'):
                with open(os.path.join(jsons_dir, filename), 'r') as f:
                    self.json_data[filename.replace('.json', '')] = json.load(f)

    def test_named_tuple(self):
        """Tests that the JSON files under /jsons are correctly parsed into NamedTuples."""
        for json_name, data in self.json_data.items():
            with self.subTest(json=json_name):
                expected_value = EXPECTED_NAMED_TUPLES.get(json_name)
                if isinstance(expected_value, list):
                    parsed_value = parse_json(data, [type(expected_value[0])])
                else:
                    parsed_value = parse_json(data, type(expected_value))
                self.assertEqual(parsed_value, expected_value)

    def test_data_class(self):
        """Tests that the JSON files under /jsons are correctly parsed into DataClasses."""
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
