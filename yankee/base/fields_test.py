import datetime
from dateutil.tz import tzutc

from .fields import * #: noqa

class TestDateTime():
    def test_dt_string(self):
        result = DateTime(dt_format="%m/%d/%Y").deserialize("03/15/2019")
        assert result == datetime.datetime(2019, 3, 15)

    def test_isoformat(self):
        dt = datetime.datetime.now()
        result = DateTime().deserialize(dt.isoformat())
        assert result == dt

    def test_bad_isoformat(self):
        field = DateTime()
        result = field.deserialize("2017-04-18T04:00:00Z")
        assert result == datetime.datetime(2017, 4, 18, 4, 0, tzinfo=tzutc())

class TestDate():
    def test_dt_string(self):
        result = Date(dt_format="%m/%d/%Y").deserialize("03/15/2019")
        assert result == datetime.date(2019, 3, 15)

    def test_isoformat(self):
        dt = datetime.datetime.now().date()
        result = Date().deserialize(dt.isoformat())
        assert result == dt

    def test_bad_isoformat(self):
        field = Date()
        result = field.deserialize("2017-04-18T04:00:00Z")
        assert result == datetime.date(2017, 4, 18)