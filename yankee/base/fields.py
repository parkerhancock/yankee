from __future__ import annotations

import datetime

from dateutil.parser import parse as parse_date
from dateutil.parser._parser import ParserError

from yankee.util import clean_whitespace, is_valid

from .deserializer import Deserializer
from .schema import Schema


class Field(Deserializer):
    def __init__(self, data_key=None, required=False, many=False):
        super().__init__(data_key=data_key, required=required)
        self.required = required

    def deserialize(self, obj):
        result = super().deserialize(obj)
        if result is None and self.required:
            raise ValueError(
                f"Field {self.name} is required! Key {self.key} not found in {obj}"
            )
        return result


class String(Field):
    def __init__(self, data_key=None, required=False, attr=None, formatter=None):
        super().__init__(data_key, required)
        self.formatter = formatter or clean_whitespace

    def deserialize(self, elem) -> "Optional[str]":
        elem = super().deserialize(elem)
        if elem is None:
            return None
        else:
            return self.formatter(self.to_string(elem))

    def to_string(self, elem):
        return str(elem)


class DateTime(String):
    def __init__(
        self, data_key=None, required=False, attr=None, formatter=None, dt_format=None
    ):
        super().__init__(data_key, required, attr, formatter)
        if dt_format:
            self.parse_date = lambda s: datetime.datetime.strftime(s, dt_format)
        else:
            self.parse_date = lambda s: datetime.datetime.fromisoformat(s)

    def deserialize(self, elem) -> "Optional[datetime.datetime]":
        string = super(DateTime, self).deserialize(elem)
        if not string:
            return None
        try:
            return self.parse_date(string)
        except ValueError as e:
            if string.endswith(
                "0229"
            ):  # Occasionally dates will be on the wrong leap year
                dt = parse_date(string[:4] + "0228", ignoretz=True)
            try:
                # Occasionally in USPTO dates in YYYYMMDD format,
                # the day and month are reversed
                return parse_date(string[:4] + string[6:8] + string[4:6], ignoretz=True)
            except ParserError:
                pass
            try:
                # Some older files have dates that are placeholders that need to be
                # converter to real dates.
                if "190000" in string:
                    dt = datetime.datetime(1900, 1, 1)
                elif string == "00000000":
                    dt = datetime.datetime(1900, 1, 1)
                elif string.endswith("0000"):
                    dt = parse_date(string[:-4] + "0101", ignoretz=True)
                elif string.endswith("00"):
                    dt = parse_date(string[-2] + "01", ignoretz=True)
                return None
            except ParserError:
                pass
            return dt


class Date(DateTime):
    def deserialize(self, elem) -> "Optional[datetime.date]":
        date_time = super().deserialize(elem)
        return date_time.date() if date_time else None


class Boolean(String):
    def __init__(
        self, *args, true_value="true", case_sensitive=False, allow_none=True, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.true_value = true_value
        self.case_sensitive = case_sensitive
        self.allow_none = allow_none
        if not self.case_sensitive:
            self.true_value = self.true_value.lower()

    def deserialize(self, elem) -> "Optional[bool]":
        string = super(Boolean, self).deserialize(elem)
        if string is None:
            return None if self.allow_none else False
        if not self.case_sensitive:
            string = string.lower()
        return string == self.true_value


class Float(String):
    def deserialize(self, elem) -> "Optional[float]":
        string = super(Float, self).deserialize(elem)
        return float(string) if string is not None else None


class Integer(String):
    def deserialize(self, elem) -> "Optional[int]":
        string = super(Integer, self).deserialize(elem)
        return int(string) if string is not None else None


class Exists(Field):
    def deserialize(self, elem) -> bool:
        obj = super(Exists, self).deserialize(elem)
        return obj is not None


class Const(Field):
    def __init__(self, const, *args, **kwargs):
        self.const = const

    def deserialize(self, elem) -> "Any":
        return self.const


# Multiple Value Field


class List(Field):
    many = True

    def __init__(self, item_schema, data_key=None, formatter=lambda l: l, **kwargs):
        super().__init__(data_key=data_key, **kwargs)
        self.formatter = formatter
        self.item_schema = item_schema
        if callable(self.item_schema):
            self.item_schema = item_schema()

    def bind(self, name, schema):
        super().bind(name, schema)
        self.item_schema.bind(None, schema)

    def deserialize(self, elem) -> "List":
        elements = super().deserialize(elem)
        if elements is None:
            return list()
        output = [self.item_schema.deserialize(e) for e in elements]
        return self.formatter([r for r in output if is_valid(r)])


# Schema-Like Fields


class Combine(Schema):
    """Can have fields like a schema that are then
    passed as an object to a combine function that
    transforms it to a single string value"""

    def bind(self, name=None, parent=None):
        super().bind(name, parent)
        for name, field in self.fields.items():
            field.bind(name, self)

    def combine_func(self, obj):
        raise NotImplementedError("Must be implemented in subclass")

    def deserialize(self, et_elem) -> "Optional[str]":
        obj = super().deserialize(et_elem)
        return self.combine_func(obj)


class Alternative(Schema):
    """There may be a piece of data that has different names
    in different contexts. This has fields like a schema, then
    passes as a value the first non-empty or non-null result"""

    def deserialize(self, et_elem):
        obj = super().deserialize(et_elem)
        return next((v for v in obj.values() if is_valid(v)), None)


class Zip(Schema):
    _list_field = List
    """Sometimes data is provided as a bunch of arrays, like:
    {
        "name": ["Peter", "Parker"],
        "age": [15, 25],
    }
    and we want to build out complete records from this data.
    This field performs that step:
    """

    def bind(self, name=None, parent=None):
        super().bind(name=name, parent=parent)
        list_fields = dict()
        if not hasattr(self, "_keys"):
            self._keys = {k: v.data_key for k, v in self.fields.items()}

        for k, v in self.fields.items():
            v.data_key = None
            list_field = self._list_field(v, data_key=self._keys[k])
            list_field.bind(k, self)
            list_fields[k] = list_field
        self.fields = list_fields

    def lists_to_records(self, obj):
        keys = tuple(obj.keys())
        values = tuple(obj.values())
        return [dict(zip(keys, v)) for v in zip(*values)]

    def deserialize(self, raw_obj) -> "Dict":
        obj = super().deserialize(raw_obj)
        return self.lists_to_records(obj)
