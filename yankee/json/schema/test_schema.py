import datetime

import pytest
import ujson as json

from yankee.json.schema import Schema, fields as f, JsonPath

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
        return f"{obj.addressLine1}\n{obj.addressLine2}"

class NameSchema(f.Combine):
    part1 = f.Str()
    part2 = f.Str()

    def combine_func(self, obj):
        return f"{obj.part1} {obj.part2}"

class SubSchema(Schema):
    string = f.Str()
    float = f.Float()

class ExampleSchema(Schema):
    string = f.Str()
    string_path = f.Str(JsonPath("string"))
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
    doc_str = json.dumps(doc)
    data = schema.load(doc_str)
    assert data.string == "Some String Data"
    assert data.date_time == datetime.datetime(2021, 5, 4, 12, 5)
    assert data.date == datetime.date(2021, 5, 4)
    assert data.booleans == [True, True, False, False]
    assert data.float - 1.234 < 0.001
    assert data.int == 23
    assert data.exists == True
    assert data.does_not_exist == False
    assert data.name == "George Burdell"
    assert data.sub.string == "Some String Data"
    assert data.address == "1234 Anywhere\nAustin, TX 71234"

def test_json_path():
    doc = {'foo': [{'baz': 1}, {'baz': 2}]}
    class PathSchema(Schema):
        numbers = f.Int(JsonPath("foo[*].baz"))
    data = PathSchema().load(doc)
    assert data.numbers == 1

    class PathListSchema(Schema):
        numbers = f.List(f.Int, JsonPath("foo[*].baz"))
    data = PathListSchema().load(doc)
    assert data.numbers == [1, 2]