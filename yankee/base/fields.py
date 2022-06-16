from __future__ import annotations

import datetime
import re
import copy

from dateutil.parser import parse as parse_dt, isoparse

from yankee.util import clean_whitespace, is_valid

from .deserializer import Deserializer
from .schema import Schema


class Field(Deserializer):
    def __init__(self, data_key=None, required=False, many=False):
        super().__init__(data_key=data_key, required=required)
        self.required = required

    def deserialize(self, obj):
        if obj is None and self.required:
            raise ValueError(
                f"Field {self.name} is required! Key {self.key} not found in {obj}"
            )
        return obj


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

    def to_string(self, elem): # Abstracted out since XML requires a function call
        return str(elem)


class DateTime(String):
    def __init__(
        self, data_key=None, required=False, attr=None, formatter=None, dt_format=None
    ):
        super().__init__(data_key, required, attr, formatter)
        if dt_format:
            self.parse_date = lambda s: datetime.datetime.strptime(s, dt_format)

    def parse_date(self, text:str):
        try:
            return isoparse(text)
        except ValueError:
            return parse_dt(text)

    def deserialize(self, elem) -> "Optional[datetime.datetime]":
        string = super(DateTime, self).deserialize(elem)
        if not string:
            return None
        return self.parse_date(string)      



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
        if string is None or string == '':
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


# Multiple Value Fields
class List(Field):
    many = True

    def __init__(self, item_schema, data_key, **kwargs):
        self.item_schema = item_schema
        if callable(self.item_schema):
            self.item_schema = item_schema()
        super().__init__(data_key, **kwargs)

    def bind(self, name=None, schema=None):
        super().bind(name, schema)
        self.item_schema.bind(None, schema)

    def deserialize(self, obj):
        obj_gen = (self.item_schema.load(i) for i in obj)
        return [o for o in obj_gen if is_valid(o)]

class Dict(List):
    """Converts a list of items into a dictionary based on
    the key and value fields passed to it.
    """
    
    def __init__(self, data_key, key:Field, value:Field, **kwargs):
        self.key = key
        self.value = value
        return super().__init__(Field(), data_key, **kwargs)
    
    def deserialize(self, obj):
        obj = super().deserialize(obj)
        return {self.key.load(i):self.value.load(i) for i in obj}

# String Parsing Fields

class DelimitedString(String):
    def __init__(self, item_schema, data_key=None, delimeter=",", **kwargs):
        self.item_schema = item_schema
        if not isinstance(delimeter, re.Pattern):
            delimeter = re.compile(delimeter)
        self.delimeter = delimeter
        if callable(self.item_schema):
            self.item_schema = item_schema()
        super().__init__(data_key=data_key, **kwargs)

    def bind(self, name=None, schema=None):
        super().bind(name, schema)
        self.item_schema.bind(None, schema)

    def deserialize(self, obj):
        obj = super().deserialize(obj)
        if obj is None:
            return None
        objs = (self.item_schema.load(o) for o in self.delimeter.split(obj))
        return [o for o in objs if is_valid(o)]



# Schema-Like Fields

class Combine(Schema):
    """Can have fields like a schema that are then
    passed as an object to a combine function that
    transforms it to a single string value"""
 

    def get_output_name(self, name):
        return name

    def combine_func(self, obj):
        raise NotImplementedError("Must be implemented in subclass")

    def deserialize(self, raw_obj) -> "Optional[str]":
        obj = super().deserialize(raw_obj)
        return self.combine_func(obj)


class Alternative(Schema):
    """There may be a piece of data that has different names
    in different contexts. This has fields like a schema, then
    passes as a value the first non-empty or non-null result"""

    def deserialize(self, et_elem):
        obj = super().deserialize(et_elem)
        return next((v for v in obj.values() if is_valid(v)), None)


class ZipSchema(Schema):
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
        super().bind(name, parent)
        zip_fields = dict()
        for k, v in self.fields.items():
            v_copy = copy.deepcopy(v)
            # Remove the data key
            data_key = v_copy.data_key
            v_copy.data_key = None
            # Place it on the list field
            zip_fields[k] = self._list_field(v_copy, data_key)
        self.unzip_fields = self.fields
        self.fields = zip_fields

    def deserialize(self, obj) -> "Dict":
        objs = super().deserialize(obj)
        return self.lists_to_records(objs)
    
    def lists_to_records(self, obj):
        keys = tuple(obj.keys())
        values = tuple(obj.values())
        return [dict(zip(keys, v)) for v in zip(*values)]
