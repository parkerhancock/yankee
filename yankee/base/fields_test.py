import pytest
import datetime
from dateutil.tz import tzutc

from .fields import * #: noqa

class TestDateTime():
    def test_dt_string(self):
        result = DateTime(dt_format="%m/%d/%Y").deserialize("03/15/2019")
        assert result == datetime.datetime(2019, 3, 15)

    def test_isoformat(self):
        dt = datetime.datetime.now()
        result = DateTime().load(dt.isoformat())
        assert result == dt

    def test_bad_isoformat(self):
        field = DateTime()
        result = field.load("2017-04-18T04:00:00Z")
        assert result == datetime.datetime(2017, 4, 18, 4, 0, tzinfo=tzutc())

class TestDate():
    def test_dt_string(self):
        result = Date(dt_format="%m/%d/%Y").load("03/15/2019")
        assert result == datetime.date(2019, 3, 15)

    def test_isoformat(self):
        dt = datetime.datetime.now().date()
        result = Date().load(dt.isoformat())
        assert result == dt

    def test_bad_isoformat(self):
        field = Date()
        result = field.load("2017-04-18T04:00:00Z")
        assert result == datetime.date(2017, 4, 18)

class TestInt():
    def test_int(self):
        field = Int()
        assert field.load("15") == 15

    def test_missing_int(self):
        field = Int()
        assert field.load("") == None
        assert field.load(None) == None

    def test_bad_int(self):
        field = Int()
        with pytest.raises(ValueError):
            field.load("Some text")

class TestFloat():
    def test(self):
        field = Float()
        assert field.load("15.24") - 15.24 < 0.001

    def test_missing(self):
        field = Float()
        assert field.load("") == None
        assert field.load(None) == None

    def test_bad(self):
        field = Float()
        with pytest.raises(ValueError):
            field.load("Some text")

class TestList():
    def test(self):
        data = [1, 2, 3]
        field = List(item_schema=Str())
        result = field.load(data)
        assert result == ["1", "2", "3"]

    def test_missing(self):
        field = List(item_schema=Str())
        result = field.load(None)
        assert result == list()