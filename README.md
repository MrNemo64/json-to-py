# json-to-py

`json-to-py` is a lightweight Python utility that simplifies converting JSON data into Python dataclass instances. It leverages Python's type annotations to ensure that JSON structures are parsed into strongly-typed Python objects, enhancing code reliability and maintainability.

## Features

- 🔍 Type-Safe Parsing: Automatically converts JSON values into instances of specified types, ensuring type correctness.

- 🧩 Nested Structure Support: Seamlessly handles nested types, allowing for complex JSON structures to be parsed effortlessly.

- 🛠️ Minimal Dependencies: Built using Python's standard libraries, eliminating the need for external packages.

## Installation

You can install json-to-py via pip:

```bash
pip install json-to-py
```

## Usage

Here's a basic example demonstrating how to use `json-to-py`:

```python
from dataclasses import dataclass
from json_to_py import parse_json

@dataclass
class Address:
    street: str
    city: str
    postal_code: str

@dataclass
class Person:
    name: str
    age: int
    address: Address

json_data = {
    "name": "Alice",
    "age": 30,
    "address": {
        "street": "123 Main St",
        "city": "Wonderland",
        "postal_code": "12345"
    }
}

person = parse_json(json_data, Person)
print(person)

# Output: Person(name='Alice', age=30, address=Address(street='123 Main St', city='Wonderland', postal_code='12345'))
```

## API Reference

### `parse_json(data: JSONType, clazz: Type[T]) -> T`

Parses a JSON-compatible value (`data`) into an instance of the specified dataclass (`clazz`).

#### Limitations

- The target class must be a
  - `str`
  - `int`
  - `float`
  - `bool`
  - `typing.Any`
  - `typing.Dict` of key type `str`
  - `typing.List`
  - `typing.Set`
  - `typing.Tuple`
  - `typing.Optional`
  - `typing.Literal` / `typing_extensions.Literal`
  - `typing.Union`
  - Dataclass
  - NamedTuple
- All fields in the dataclass/namedtuple must be type-annotated
- Setting default values

#### Features

- Works with Python 3.7+
- Have different names in the json from a dataclass:
  ```python
  @dataclass
  class Example():
      a_number: int = field(metadata={"json-to-py": "a-number"})
  ```
  Here, the key in the JSON must be `a-number` instead of an `a_number`.
- Support for `typing.Dict`:
  - The key type has to be `str`, the value can be any of the listed in the limitations section
- Support for `typing.List`:
  - The list type can be any of the listed in the limitations section
- Support for `typing.Set`:
  - Interpreted as a JSON array
  - The set type must be any of the listed in the limitations section
- Support for `typing.Tuple`:
  - Interpreted as a JSON array with a fixed amount of elements
  - The tuple types must be any of the listed in the limitations section
- Support for `typing.Literal` / `typing_extensions.Literal`:
  - Checks if the JSON value is in the literal list of values
- Support for `typing.Union`
  - The union types must be any of the listed in the limitations section
  - To parse unions, the first type defined in the union is assumed to be the correct one and attemped to parse. If this fails, the next type is tryed until there are no more types or one succeeds

## More complex example

See the example below for an example with versioning and lots of features

```python
class UserInformation(NamedTuple):
    name: str
    age: int

data = {
    "name": "Nemo",
    "age": 64
}
print(parse_json(data), UserInformation)
# UserInformation(
#   name='Nemo',
#   age=64
# )

class UserInformation_v2(NamedTuple):
    version: Literal["1.2"] # Added to differenciate between versions
    name: str
    surenames: List[str] # Added
    age: int

data = {
    "version": "1.2",
    "name": "Nemo",
    "surenames": ["First", "Seccond"],
    "age": 64
}
print(parse_json(data), Union[UserInformation_v2, UserInformation])
# UserInformation_v2(
#   version='1.2',
#   name='Nemo',
#   surenames=['First', 'Seccond'],
#   age=64
# )

class UserInformation_v3(NamedTuple):
    version: Literal["1.3"]
    name: List[str] # Merged name with surenames
    age: float # Changed from int to float

data = {
    "version": "1.3",
    "name": ["Nemo", "First", "Seccond"],
    "age": 64.5
}
print(parse_json(data), Union[UserInformation_v3, UserInformation_v2, UserInformation])
# UserInformation_v3(
#   version='1.3',
#   name=['Nemo', 'First', 'Seccond'],
#   age=64.5
# )

@dataclass # Switched to dataclass
class UserInformation_v4():
    version: Literal["1.4"]
    id: str # Added
    name: List[str]
    age: float
    relations: List[str] # Added

data = {
    "version": "1.4",
    "id": "id123",
    "name": ["Nemo", "First", "Seccond"],
    "age": 64.5,
    "relations": ["id456"]
}
print(parse_json(data), Union[UserInformation_v4, UserInformation_v3, UserInformation_v2, UserInformation])
# UserInformation_v4(
#   version='1.4',
#   id='id123',
#   name=['Nemo', 'First', 'Seccond'],
#   age=64.5,
#   relations=['id456']
# )

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

data = {
    "version": "1.5",
    "id": "id123",
    "name": ["Nemo", "First", "Seccond"],
    "age": 64.5,
    "relations": ["id456"]
}
print(parse_json(data), Union[UserInformation_v5, UserInformation_v4, UserInformation_v3, UserInformation_v2, UserInformation])
# UserInformation_v5(
#   version='1.5',
#   id='id123',
#   name=['Nemo', 'First', 'Seccond'],
#   age=64.5,
#   relations=[
#       UserRelation(user='id456', relation_type='friend')
#   ]
# )

@dataclass
class UserInformation_v6():
    version: Literal["1.6"]
    id: str
    name: List[str]
    age: float
    relations: List[UserRelation]
    extra_information: Dict[str, str] = field(metadata={"json-to-py": {"name": "extra-information"}}) # Added. Will apprear in the json as 'extra-information'

data = {
    "version": "1.6",
    "id": "id123",
    "name": ["Nemo", "First", "Seccond"],
    "age": 64.5,
    "relations": [{"user": "id456", "relation-type": "friend"}],
    "extra-information": {"extra": "info"}
}
print(parse_json(data), Union[UserInformation_v6, UserInformation_v5, UserInformation_v4, UserInformation_v3, UserInformation_v2, UserInformation])
# UserInformation_v6(
#   version='1.6',
#   id='id123',
#   name=['Nemo', 'First', 'Seccond'],
#   age=64.5,
#   relations=[
#       UserRelation(user='id456', relation_type='friend')
#   ],
#   extra_information={
#       'extra': 'info'
#    }
# )

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

data = {
    "version": "1.7",
    "id": "id123",
    "name": ["Nemo", "First", "Seccond"],
    "age": 64.5,
    "relations": [{"version": "1.2", "user": "id456", "since": "11-05-2025", "relation-type": "friend"}],
    "extra-information": [{"name": "a string", "value": "string value"}, {"name": "an int", "value": 987}, {"name": "a bool", "value": True}]
}
print(parse_json(data), Union[UserInformation_v7, UserInformation_v6, UserInformation_v5, UserInformation_v4, UserInformation_v3, UserInformation_v2, UserInformation])
# UserInformation_v7(
#   version='1.7',
#   id='id123',
#   name=['Nemo', 'First', 'Seccond'],
#   age=64.5,
#   relations=[
#       UserRelation_v2(version='1.2', user='id456', since='11-05-2025', relation_type='friend')
#   ],
#   extra_information=[
#       UserFieldStr(name='a string', value='string value'),
#       UserFieldInt(name='an int', value=987),
#       UserFieldBool(name='a bool', value=True)
#   ]
# )
```
