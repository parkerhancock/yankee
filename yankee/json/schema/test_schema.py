import datetime
import pytest
from .schema import Schema
from .fields import *

doc = {
    "string": "Some String Data",
    "date_time": "2021-05-04T12:05",
    "date": "2021-05-04",
    "booleans": [
        "True",
        "true",
        "False",
        "false"
    ],
    "float": 1.234,
    "int": 23,
    "exists": "Something",
    "name": {
        "part1": "George",
        "part2": "Burdell"
    },
    "random": "Some data",
    "first_name": ['Peter', 'Parker'],
    "age": [15, 21],
}

class Name(Combine):
    part1 = Str()
    part2 = Str()

    def combine_func(self, obj):
        return f"{obj['part1']} {obj['part2']}"

class Person(Zip):
    first_name = Str()
    age = Int()

class ExampleSchema(Schema):
    string = Str()
    date_time = DT()
    date = Date()
    booleans = List(Bool, data_key="booleans")
    float = Float()
    int = Int()
    exists = Exists()
    does_not_exist = Exists()
    name = Name()
    people = Person(None)

def test_fields():
    data = ExampleSchema().deserialize(doc)
    assert data['string'] == "Some String Data"
    assert data['dateTime'] == datetime.datetime(2021, 5, 4, 12, 5)
    assert data['date'] == datetime.date(2021, 5, 4)
    assert data['booleans'] == [True, True, False, False]
    assert data['float'] - 1.234 < 0.001
    assert data['int'] == 23
    assert data['exists'] == True
    assert data['doesNotExist'] == False
    assert data['name'] == "George Burdell"
    assert data['people'][0] == {"first_name": "Peter", "age": 15}