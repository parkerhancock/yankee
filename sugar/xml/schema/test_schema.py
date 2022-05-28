import datetime
import pytest
import lxml.etree as ET
from .schema import Schema
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

class Name(Combine):
    part1 = Str("./part1")
    part2 = Str("./part2")

    def combine_func(self, obj):
        return f"{obj['part1']} {obj['part2']}"

class TestSchema(Schema):
    string = Str("./string")
    date_time = DT("./date_time")
    date = Date("./date")
    booleans = List(Bool, key="./booleans/bool")
    float = Float("./float")
    int = Int("./int")
    exists = Exists("./exists")
    does_not_exist = Exists("./does_not_exist")
    name = Name()

def test_fields():
    data = TestSchema().deserialize(tree)
    assert data['string'] == "Some String Data"
    assert data['date_time'] == datetime.datetime(2021, 5, 4, 12, 5)
    assert data['date'] == datetime.date(2021, 5, 4)
    assert data['booleans'] == [True, True, False, False]
    assert data['float'] - 1.234 < 0.001
    assert data['int'] == 23
    assert data['exists'] == True
    assert data['does_not_exist'] == False
    assert data['name'] == "George Burdell"