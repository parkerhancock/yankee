import datetime

import lxml.etree as ET
import pytest

from yankee.xml import Schema
from yankee.xml import fields as f
from yankee.xml.schema.schema import RegexSchema

from .fields import *

test_doc = """
<testDoc>
    <string>Some String Data</string>
    <regex>data_a;data_b</regex>
    <date_time>2021-05-04T12:05</date_time>
    <date>2021-05-04</date>
    <booleans>
        <bool>True</bool>
        <bool>true</bool>
        <bool>False</bool>
        <bool>false</bool>
        <bool/>
    </booleans>
    <float>1.234</float>
    <int>23</int>
    <exists>Something</exists>
    <part1>George</part1>
    <part2>Burdell</part2>
    <random>Some data</random>
    <csv>name1,name2,name3</csv>
</testDoc>
""".strip()


tree = ET.fromstring(test_doc.encode())
class NameSchema(Combine):
    part1 = f.Str("./part1")
    part2 = f.Str("./part2")

    def combine_func(self, obj):
        return f"{obj['part1']} {obj['part2']}"

class RegexExample(RegexSchema):
    a = f.Str("./a")
    b = f.Str("./b")
    
    __regex__ = r"(?P<a>[^;]+);(?P<b>[^;]+)"


class ExampleSchema(Schema):
    string = f.Str("./string")
    other_string = f.Str("./string/text()")
    date_time = f.DT("./date_time")
    date = f.Date("./date")
    booleans = f.List(Bool, "./booleans/bool")
    float = f.Float("./float")
    int = f.Int("./int")
    exists = f.Exists("./exists")
    does_not_exist = f.Exists("./does_not_exist")
    name = NameSchema()
    regex = RegexExample("./regex")
    bad_regex = RegexExample("./missing")
    gone = f.Str("./nonexistent_path")
    csv = f.DelimitedString(f.Str(), data_key="./csv", delimeter=",")



def test_fields():
    d = ExampleSchema()
    data = d.deserialize(tree)
    assert data["string"] == "Some String Data"
    assert data["date_time"] == datetime.datetime(2021, 5, 4, 12, 5)
    assert data["date"] == datetime.date(2021, 5, 4)
    assert data["booleans"] == [True, True, False, False]
    assert data["float"] - 1.234 < 0.001
    assert data["int"] == 23
    assert data["exists"] == True
    assert data["does_not_exist"] == False
    assert data["name"] == "George Burdell"
    assert data['regex']['a'] == 'data_a'
    assert data['regex']['b'] == 'data_b'
    assert 'gone' not in data
    assert data['csv'] == ['name1', 'name2', 'name3']

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
    data = d.load(ns_tree)
    assert data["string"] == "Some String Data"
    assert data["date_time"] == datetime.datetime(2021, 5, 4, 12, 5)
    assert data["date"] == datetime.date(2021, 5, 4)
    assert data["booleans"] == [True, True, False, False]
