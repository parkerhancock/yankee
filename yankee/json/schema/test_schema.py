import datetime

import pytest

from yankee.json import Schema, ZipSchema
from yankee.json import fields as f

doc = {
    "string": "Some String Data",
    "date_time": "2021-05-04T12:05",
    "date": "2021-05-04",
    "booleans": ["True", "true", "False", "false"],
    "float": 1.234,
    "int": 23,
    "exists": "Something",
    "name": {"part1": "George", "part2": "Burdell"},
    "random": "Some data",
    "first_name": ["Peter", "Parker"],
    "age": [15, 21],
}


class NameSchema(f.Combine):
    part1 = f.Str()
    part2 = f.Str()

    def combine_func(self, obj):
        return f"{obj['part1']} {obj['part2']}"


class PersonSchema(ZipSchema):
    first_name = f.Str()
    age = f.Int()


class ExampleSchema(Schema):
    string = f.Str()
    date_time = f.DT()
    date = f.Date()
    booleans = f.List(f.Bool, data_key="booleans")
    float = f.Float()
    int = f.Int()
    exists = f.Exists()
    does_not_exist = f.Exists()
    name = NameSchema()
    people = PersonSchema(data_key=False)


def test_fields():
    data = ExampleSchema().deserialize(doc)
    assert data["string"] == "Some String Data"
    assert data["dateTime"] == datetime.datetime(2021, 5, 4, 12, 5)
    assert data["date"] == datetime.date(2021, 5, 4)
    assert data["booleans"] == [True, True, False, False]
    assert data["float"] - 1.234 < 0.001
    assert data["int"] == 23
    assert data["exists"] == True
    assert data["doesNotExist"] == False
    assert data["name"] == "George Burdell"
    assert data["people"][0] == {"firstName": "Peter", "age": 15}
