import datetime

import pytest

from yankee.json import Schema
from yankee.json import fields as f

doc = {
    "string": "Some String Data",
    "dateTime": "2021-05-04T12:05",
    "date": "2021-05-04",
    "booleans": ["True", "true", "False", "false"],
    "float": 1.234,
    "int": 23,
    "exists": "Something",
    "name": {"part1": "George", "part2": "Burdell"},
    "random": "Some data",
    "addressLine1": "1234 Anywhere",
    "addressLine2": "Austin, TX 71234",
}

class AddressField(f.Combine):
    addressLine1 = f.Str()
    addressLine2 = f.Str()

    def combine_func(self, obj):
        return f"{obj['addressLine1']}\n{obj['addressLine2']}"

class NameSchema(f.Combine):
    part1 = f.Str()
    part2 = f.Str()

    def combine_func(self, obj):
        return f"{obj['part1']} {obj['part2']}"

class SubSchema(Schema):
    string = f.Str()
    float = f.Float()

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
    sub = SubSchema(False)
    address = AddressField(False)
    


def test_fields():
    schema = ExampleSchema()
    data = schema.load(doc)
    assert data["string"] == "Some String Data"
    assert data["date_time"] == datetime.datetime(2021, 5, 4, 12, 5)
    assert data["date"] == datetime.date(2021, 5, 4)
    assert data["booleans"] == [True, True, False, False]
    assert data["float"] - 1.234 < 0.001
    assert data["int"] == 23
    assert data["exists"] == True
    assert data["does_not_exist"] == False
    assert data["name"] == "George Burdell"
    assert data['sub']['string'] == "Some String Data"
    assert data['address'] == "1234 Anywhere\nAustin, TX 71234"