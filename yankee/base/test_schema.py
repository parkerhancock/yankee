import datetime

import pytest

from yankee import Schema, fields as f

doc1 = {
    "string": "Some String Data",
    "date_time": "2021-05-04T12:05",
    "date": "2021-05-04",
    "booleans": ["True", "true", "False", "false"],
    "float": 1.234,
    "int": 23,
    "exists": "Something",
    "name": {"part1": "George", "part2": "Burdell"},
    "random": "Some data",
    "address_line_1": "1234 Anywhere",
    "address_line_2": "Austin, TX 71234",
    "bad_string": "",
}

def to_obj(obj):
    if isinstance(obj, dict):
        return type("Dict", (object,), {k: to_obj(v) for k, v in obj.items()})
    elif isinstance(obj, list):
        return [to_obj(i) for i in obj]
    else:
        return obj

doc2 = to_obj(doc1)

class AddressField(f.Combine):
    address_line_1 = f.Str()
    address_line_2 = f.Str()

    def combine_func(self, obj):
        return f"{obj.address_line_1}\n{obj.address_line_2}"

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
    bad_string = f.Str()



def test_fields_on_dict():
    schema = ExampleSchema()
    data = schema.load(doc1)
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
    assert "bad_string" not in data

def test_fields_on_obj():
    schema = ExampleSchema()
    data = schema.load(doc2)
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
    assert "bad_string" not in data

class JsonExampleSchema(Schema):
    class Meta:
        output_style = "json"
    string = f.Str()
    date_time = f.DT()
    date = f.Date()

def test_json_output_type():
    schema = JsonExampleSchema()
    data = schema.load(doc2)
    assert data['string'] == "Some String Data"
    assert data['dateTime'] == "2021-05-04T12:05:00"
    assert data['date'] == "2021-05-04"

class SecondSchema(Schema):
    first_schema = f.Nested("FirstSchema", data_key=False)

class FirstSchema(Schema):
    string = f.Str()

delayed_data_doc = {
    "string": "Some String"
}

def test_delayed_imports():
    schema = SecondSchema()
    data = schema.load(delayed_data_doc)
    assert data == {"first_schema": {"string": "Some String"}}

class ListSchema(Schema):
    l = f.List("ItemSchema")

class ItemSchema(Schema):
    i = f.Str()

delayed_list_doc = {
    "l": [
        {"i": "string1"},
        {"i":"string2"}
    ]
}

def test_list_field_by_string():
    schema = ListSchema()
    data = schema.load(delayed_list_doc)
    assert data == delayed_list_doc

