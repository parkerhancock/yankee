import datetime

import lxml.etree as ET
import pytest

from yankee.xml import Schema, ZipSchema
from yankee.xml import fields as f

from .fields import *

test_doc = """
<testDoc>
    <string>Some String Data</string>
    <date_time>2021-05-04T12:05</date_time>
    <date>2021-05-04</date>
    <booleans>
        <bool>True</bool>
        <bool>true</bool>
        <bool>False</bool>
        <bool>false</bool>
    </booleans>
    <float>1.234</float>
    <int>23</int>
    <exists>Something</exists>
    <part1>George</part1>
    <part2>Burdell</part2>
    <random>Some data</random>
</testDoc>
""".strip()


tree = ET.fromstring(test_doc.encode())
class NameSchema(Combine):
    part1 = f.Str("./part1")
    part2 = f.Str("./part2")

    def combine_func(self, obj):
        return f"{obj['part1']} {obj['part2']}"
class ExampleSchema(Schema):
    string = f.Str("./string")
    date_time = f.DT("./date_time")
    date = f.Date("./date")
    booleans = f.List(Bool, "./booleans/bool")
    float = f.Float("./float")
    int = f.Int("./int")
    exists = f.Exists("./exists")
    does_not_exist = f.Exists("./does_not_exist")
    name = NameSchema()


def test_fields():
    d = ExampleSchema()
    data = d.deserialize(tree)
    assert data["string"] == "Some String Data"
    assert data["dateTime"] == datetime.datetime(2021, 5, 4, 12, 5)
    assert data["date"] == datetime.date(2021, 5, 4)
    assert data["booleans"] == [True, True, False, False]
    assert data["float"] - 1.234 < 0.001
    assert data["int"] == 23
    assert data["exists"] == True
    assert data["doesNotExist"] == False
    assert data["name"] == "George Burdell"

ns_test_doc = """
<?xml version='1.0' encoding='UTF-8'?>
<h:testDoc xmlns:h="http:www.w3.org/TR/html4/">
    <h:string>Some String Data</h:string>
    <h:date_time>2021-05-04T12:05</h:date_time>
    <h:date>2021-05-04</h:date>
    <h:booleans>
        <bool>True</bool>
        <bool>true</bool>
        <bool>False</bool>
        <bool>false</bool>
    </h:booleans>
</h:testDoc>
""".strip()

ns_tree = ET.fromstring(ns_test_doc.encode())

class NsSchema(Schema):
    class Meta():
        namespaces = {
            "h": "http:www.w3.org/TR/html4/"
        }
    string = f.Str("./h:string")
    date_time = f.DT("./h:date_time")
    date = f.Date("./h:date")
    booleans = f.List(Bool, "./h:booleans/bool")
   
def test_ns_fields():
    d = NsSchema()
    data = d.deserialize(ns_tree)
    assert data["string"] == "Some String Data"
    assert data["dateTime"] == datetime.datetime(2021, 5, 4, 12, 5)
    assert data["date"] == datetime.date(2021, 5, 4)
    assert data["booleans"] == [True, True, False, False]
