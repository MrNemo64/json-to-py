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
    Item = module.Item
    Product = module.Product
    OrderList = module.OrderList
    OrderSet = module.OrderSet
    OrderDict = module.OrderDict
    Status = module.Status

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
        "union_type_str": Item(id=1, value="apple"),
        "union_type_float": Item(id=1, value=10.5),
        "list_of_complex_type": OrderList(
            id=1,
            products=[
                Product(name="Laptop", price=999.99),
                Product(name="Mouse", price=49.99)
            ]
        ),
        "set_of_complex_type": OrderSet(
            id = 1,
            products = {
                Product(name="Laptop", price=999.99),
                Product(name="Mouse", price=49.99)
            }
        ),
        "dict_of_complex_type": OrderDict(
            id = 1,
            products = {
                "product1": Product(name="Laptop", price=999.99),
                "product2": Product(name="Mouse", price=49.99)
            }
        ),
        "literal_active": Status(status="active"),
        "literal_inactive": Status(status="inactive")
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
