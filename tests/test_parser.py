import sys

if sys.version_info < (3, 8):
    from typing_extensions import Literal
else:
    from typing import Literal
    
from typing import Dict, List, NamedTuple, Set, Tuple, Union
import unittest
import os
import json
from json_to_py.type_information import *
from json_to_py import parse_json
from json_to_py.parser import CanNotParseTypeException, NoLiteralVariantException, UnexpectedTypeException, InvalidTupleSizeException, NonStringKeyException, NoUnionVariantException
from dataclasses import dataclass, field

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

    def test_literals_as_versioning(self):
        class MyClass(NamedTuple):
            x: int
            y: int
        class MyClass2(NamedTuple):
            version: Literal["1.1"]
            x: int
            y: int
            z: int
        class MyClass3(NamedTuple):
            version: Literal["2.0"]
            x: float
            y: float
            z: float
        clazz = Union[MyClass3, MyClass2, MyClass]

        self.assertEqual(parse_json({"x": 1, "y": 2}, clazz), MyClass(1, 2))
        self.assertEqual(parse_json({"version": "1.1", "x": 1, "y": 2, "z": 3}, clazz), MyClass2("1.1", 1, 2, 3))
        self.assertEqual(parse_json({"version": "2.0", "x": 1.0, "y": 2.0, "z": 3.0}, clazz), MyClass3("2.0", 1.0, 2.0, 3.0))
        
        with self.assertRaises(NoUnionVariantException) as cm:
            parse_json({"version": "3.0", "x": 1.0, "y": 2.0, "z": 3.0}, clazz)

        ex = cm.exception
        self.assertEqual(len(ex.exceptions), 3)
        self.assertIs(type(ex.exceptions[0]), NoLiteralVariantException)
        self.assertIs(type(ex.exceptions[1]), NoLiteralVariantException)
        self.assertIs(type(ex.exceptions[2]), UnexpectedTypeException)

    def test_new_unions(self):
        if sys.version_info < (3, 10):
            return
        self.assertEqual(parse_json("a string", int | bool | str), "a string")

    def test_invalid_json(self):
        """Test for an invalid json"""
        @dataclass
        class MyDeeperClass():
            a: int
            b: int
            d: Dict[str, List[int]]
        @dataclass
        class MyClass():
            x: int
            y: int
            c: MyDeeperClass
        
        with self.assertRaises(UnexpectedTypeException) as cm:
            parse_json({
                "x": 123,
                "y": 456,
                "c": {
                    "a": 789,
                    "b": 101112,
                    "d": {
                        "i": [131415],
                        "j": [161718],
                        "k": [192021, "a string that should be an int"]
                    }
                }
            }, MyClass)
        ex = cm.exception
        self.assertEqual("a string that should be an int", ex.actual_value)
        self.assertIs(int, ex.expected_type)
        self.assertEqual(["c", "d", "k", 1], ex.json_path)
        self.assertEqual("c.d.k[1]", ex.full_path)

class TestParseJsonFailures(unittest.TestCase):

    def test_str_type_mismatch(self):
        with self.assertRaises(UnexpectedTypeException) as cm:
            parse_json(123, str)
        e = cm.exception
        self.assertEqual(e.actual_value, 123)
        self.assertEqual(e.expected_type, str)
        self.assertEqual(e.json_path, [])
    
    def test_int_type_mismatch(self):
        with self.assertRaises(UnexpectedTypeException) as cm:
            parse_json("not an int", int)
        e = cm.exception
        self.assertEqual(e.actual_value, "not an int")
        self.assertEqual(e.expected_type, int)
        self.assertEqual(e.json_path, [])

    def test_float_type_mismatch(self):
        with self.assertRaises(UnexpectedTypeException) as cm:
            parse_json("1.0", float)
        e = cm.exception
        self.assertEqual(e.actual_value, "1.0")
        self.assertEqual(e.expected_type, float)
        self.assertEqual(e.json_path, [])

    def test_bool_type_mismatch(self):
        with self.assertRaises(UnexpectedTypeException) as cm:
            parse_json("True", bool)
        e = cm.exception
        self.assertEqual(e.actual_value, "True")
        self.assertEqual(e.expected_type, bool)

    def test_list_type_mismatch(self):
        with self.assertRaises(UnexpectedTypeException) as cm:
            parse_json("not a list", List[int])
        e = cm.exception
        self.assertEqual(e.expected_type, list)

    def test_dict_type_mismatch(self):
        with self.assertRaises(UnexpectedTypeException) as cm:
            parse_json("{}", Dict[str, int])
        e = cm.exception
        self.assertEqual(e.expected_type, dict)

    def test_dict_key_nonstring(self):
        with self.assertRaises(NonStringKeyException) as cm:
            parse_json({"a": 1}, Dict[int, int])
        e = cm.exception
        self.assertEqual(e.key_clazz, int)

    def test_set_type_mismatch(self):
        with self.assertRaises(UnexpectedTypeException) as cm:
            parse_json("not a list", Set[int])
        e = cm.exception
        self.assertEqual(e.expected_type, list)

    def test_tuple_wrong_length(self):
        with self.assertRaises(InvalidTupleSizeException) as cm:
            parse_json([1], Tuple[int, str])
        e = cm.exception
        self.assertEqual(e.tuple_size, 2)

    def test_union_no_match(self):
        with self.assertRaises(NoUnionVariantException) as cm:
            parse_json(True, Union[int, str])
        e = cm.exception
        self.assertEqual(e.union_variants, (int, str))
        self.assertEqual(e.actual_value, True)
        self.assertTrue(len(e.exceptions) == 2)

    def test_literal_mismatch(self):
        with self.assertRaises(NoLiteralVariantException) as cm:
            parse_json("nope", Literal["a", "b"])
        e = cm.exception
        self.assertIn("nope", str(e))
        self.assertEqual(e.varian_values, ("a", "b"))

    def test_unknown_type(self):
        class CustomClass: pass
        with self.assertRaises(CanNotParseTypeException) as cm:
            parse_json({}, CustomClass)
        e = cm.exception
        self.assertEqual(e.clazz, CustomClass)
        self.assertEqual(e.actual_value, {})

class TestExamples(unittest.TestCase):
    def test_complex_example(self):
        class UserInformation(NamedTuple):
            name: str
            age: int

        class UserInformation_v2(NamedTuple):
            version: Literal["1.2"] # Added to differenciate between versions
            name: str
            surenames: List[str] # Added
            age: int

        class UserInformation_v3(NamedTuple):
            version: Literal["1.3"]
            name: List[str] # Merged name with surenames
            age: float # Changed from int to float

        @dataclass # Switched to dataclass
        class UserInformation_v4():
            version: Literal["1.4"]
            id: str # Added
            name: List[str]
            age: float
            relations: List[str] # Added
        
        @dataclass
        class UserRelation():
            user: str
            relation_type: str = field(metadata={"json-to-py": {"name": "relation-type"}}) # Will apprear in the json as 'relation-type'

        @dataclass
        class UserInformation_v5():
            version: Literal["1.5"]
            id: str
            name: List[str]
            age: float
            relations: List[UserRelation] # Changed to UserRelation
        
        @dataclass
        class UserInformation_v6():
            version: Literal["1.6"]
            id: str
            name: List[str]
            age: float
            relations: List[UserRelation]
            extra_information: Dict[str, str] = field(metadata={"json-to-py": {"name": "extra-information"}}) # Added. Will apprear in the json as 'extra-information'

        @dataclass
        class UserRelation_v2():
            version: Literal["1.2"] # Added to differenciate between versions
            user: str
            since: str
            relation_type: str = field(metadata={"json-to-py": {"name": "relation-type"}})

        class UserFieldInt(NamedTuple):
            name: str
            value: int

        class UserFieldStr(NamedTuple):
            name: str
            value: str

        class UserFieldBool(NamedTuple):
            name: str
            value: bool

        @dataclass
        class UserInformation_v7():
            version: Literal["1.7"]
            id: str
            name: List[str]
            age: float
            relations: List[UserRelation_v2] # Changed
            extra_information: List[Union[UserFieldInt, UserFieldStr, UserFieldBool]] = field(metadata={"json-to-py": {"name": "extra-information"}}) # Changed
        
        all_user_info = Union[UserInformation_v7, UserInformation_v6, UserInformation_v5, UserInformation_v4, UserInformation_v3, UserInformation_v2, UserInformation]

        self.assertEqual(parse_json({
            "name": "Nemo",
            "age": 64
            }, all_user_info), UserInformation("Nemo", 64))
        self.assertEqual(parse_json({
            "version": "1.2",
            "name": "Nemo",
            "surenames": ["First", "Seccond"],
            "age": 64
            }, all_user_info), UserInformation_v2("1.2", "Nemo", ["First", "Seccond"], 64))
        self.assertEqual(parse_json({
            "version": "1.3",
            "name": ["Nemo", "First", "Seccond"],
            "age": 64.5
            }, all_user_info), UserInformation_v3("1.3", ["Nemo", "First", "Seccond"], 64.5))
        self.assertEqual(parse_json({
            "version": "1.4",
            "id": "id123",
            "name": ["Nemo", "First", "Seccond"],
            "age": 64.5,
            "relations": ["id456"]
            }, all_user_info), UserInformation_v4("1.4", "id123", ["Nemo", "First", "Seccond"], 64.5, ["id456"]))
        self.assertEqual(parse_json({
            "version": "1.5",
            "id": "id123",
            "name": ["Nemo", "First", "Seccond"],
            "age": 64.5,
            "relations": [{"user": "id456", "relation-type": "friend"}]
            }, all_user_info), UserInformation_v5("1.5", "id123", ["Nemo", "First", "Seccond"], 64.5, [UserRelation("id456", "friend")]))
        self.assertEqual(parse_json({
            "version": "1.6",
            "id": "id123",
            "name": ["Nemo", "First", "Seccond"],
            "age": 64.5,
            "relations": [{"user": "id456", "relation-type": "friend"}],
            "extra-information": {"extra": "info"}
            }, all_user_info), UserInformation_v6("1.6", "id123", ["Nemo", "First", "Seccond"], 64.5, [UserRelation("id456", "friend")], {"extra": "info"}))
        self.assertEqual(parse_json({
            "version": "1.7",
            "id": "id123",
            "name": ["Nemo", "First", "Seccond"],
            "age": 64.5,
            "relations": [{"version": "1.2", "user": "id456", "since": "11-05-2025", "relation-type": "friend"}],
            "extra-information": [{"name": "a string", "value": "string value"}, {"name": "an int", "value": 987}, {"name": "a bool", "value": True}]
            }, all_user_info), UserInformation_v7("1.7", "id123", ["Nemo", "First", "Seccond"], 64.5, [UserRelation_v2("1.2", "id456", "11-05-2025", "friend")], [UserFieldStr("a string", "string value"), UserFieldInt("an int", 987), UserFieldBool("a bool", True)]))
        

if __name__ == "__main__":
    unittest.main()
