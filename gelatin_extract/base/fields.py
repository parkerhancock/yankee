from __future__ import annotations

import datetime

from dateutil.parser import parse as parse_date
from dateutil.parser._parser import ParserError

from gelatin_extract.util import clean_whitespace, is_valid
from .deserializer import Deserializer
from .schema import Schema

class Field(Deserializer):
    def __init__(self, key=None, required=False, many=False):
        super().__init__(key)
        self.required = required

    def deserialize(self, obj):
        result = super().deserialize(obj)
        if not result and self.required:
            raise ValueError(f"Field {self.name} is required! Key {self.key} not found in {obj}")
        return result
    
class String(Field):
    def __init__(self, key=None, required=False, attr=None, formatter=None):
        super().__init__(key, required)
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
    def __init__(self, key=None, required=False, attr=None, formatter=None, dt_format=None):
        super().__init__(key, required, attr, formatter)
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
            if string.endswith("0229"): # Occasionally dates will be on the wrong leap year
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
                    dt = datetime.datetime(1900,1,1)
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
    def deserialize(self, elem) -> "Optional[bool]":
        string = super(Boolean, self).deserialize(elem)
        return string.lower() == "true" if string is not None else None

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

    def __init__(self, item_schema, *args, formatter=lambda l: l, **kwargs):
        super().__init__(*args, **kwargs)
        self.formatter = formatter
        self.item_schema = item_schema
        if callable(self.item_schema):
            self.item_schema = item_schema()

    def bind(self, name, schema, meta):
        super().bind(name, schema, meta)
        self.item_schema.bind(None, schema, meta)

    def deserialize(self, elem) -> "List":
        if elem is None:
            return list()
        elements = self.key_func(elem)
        output = [self.item_schema.deserialize(e) for e in elements]
        return self.formatter([r for r in output if is_valid(r)])

# Schema-Like Fields

class Combine(Schema):
    """Can have fields like a schema that are then
    passed as an object to a combine function that 
    transforms it to a single string value"""

    class Meta:
        output_style = None

    def bind(self, name=None, parent=None, meta=None):
        super().bind(name, parent, meta)
        for name, field in self.fields.items():
            field.bind(name, self, None)

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