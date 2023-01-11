from __future__ import annotations

import datetime
import re
import importlib

from dateutil.parser import parse as parse_dt, isoparse

from yankee.util import AttrDict, clean_whitespace, is_valid

from .deserializer import Deserializer
from .schema import Schema


class Field(Deserializer):
    pass

class String(Field):
    def __init__(self, *args, formatter=None, null_value=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.formatter = formatter or clean_whitespace
        self.null_value = null_value

    def deserialize(self, elem) -> "Optional[str]":
        elem = super().deserialize(elem)
        if elem is None or elem == "" or elem == self.null_value:
            return None
        else:
            return self.formatter(self.to_string(elem))

    def to_string(self, elem): # Abstracted out since XML requires a function call
        return str(elem)


class DateTime(String):
    def __init__(self, *args, dt_format=None, **kwargs):
        super().__init__(*args, **kwargs)
        if dt_format:
            self.parse_date = lambda s: datetime.datetime.strptime(s, dt_format)

    def parse_date(self, text:str):
        try:
            return isoparse(text)
        except ValueError:
            return parse_dt(text)

    def deserialize(self, elem) -> "Optional[datetime.datetime]":
        string = super(DateTime, self).deserialize(elem)
        return self.parse_date(string) if string else None

    def post_load(self, obj):
        if self.Meta.output_style == "json":
            return obj.isoformat()
        return obj

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
        super().__init__(self, *args, **kwargs)
        self.const = const

    def deserialize(self, elem) -> "Any":
        return self.const
    

# Multiple Value Fields
    
class Nested(Schema):
    def __init__(self, schema, *args, **kwargs):
        self._schema = schema
        self._args = args
        self._kwargs = kwargs

    # Deserialize Methods
    def bind(self, name=None, parent=None):
        super().bind(name=name, parent=parent)
        if isinstance(self._schema, str):
            *module, _schema = self._schema.split(".")
            module = ".".join(module) or parent.__module__
            schema_class = getattr(importlib.import_module(module), _schema)
            self._schema = schema_class(*self._args, **self._kwargs)
        self._schema.bind(name, parent)

    def make_accessor(self, *args, **kwargs):
        if isinstance(self._schema, str):
            return
        return self._schema.make_accessor(*args, **kwargs)

    def load(self, obj):
        return self._schema.load(obj)

class List(Field):
    def __init__(self, item_schema, data_key=None, **kwargs):
        kwargs['many'] = True
        self.item_schema = item_schema
        if callable(self.item_schema):
            self.item_schema = item_schema()
        super().__init__(data_key, **kwargs)

    def bind(self, name=None, schema=None):
        super().bind(name, schema)
        if isinstance(self.item_schema, str):
            *module, _schema = self.item_schema.split(".")
            if module:
                module = ".".join(module)
            elif schema is not None:
                module = schema.__module__
            else:
                return
            self.item_schema = getattr(importlib.import_module(module), self.item_schema)()
        self.item_schema.bind(None, schema)

    def deserialize(self, obj):
        obj = super().deserialize(obj)
        if not obj:
            return list()
        obj_gen = (self.item_schema.load(i) for i in obj)
        return [o for o in obj_gen if is_valid(o)]

class Dictionary(List):
    """Converts a list of items into a dictionary based on
    the key and value fields passed to it.
    """
    
    def __init__(self, data_key, key:Field, value:Field, **kwargs):
        self.key = key
        self.value = value
        return super().__init__(Field(), data_key, **kwargs)
    
    def deserialize(self, obj):
        obj = super().deserialize(obj)
        return AttrDict((self.key.load(i), self.value.load(i)) for i in obj)

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

    def bind(self, name=None, parent=None):
        super().bind(name, parent)
        for field in self.fields.values():
            field.output_name = field.name

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


# Aliases
Str = String
DT = DateTime
Bool = Boolean
Int = Integer
Alt = Alternative
Dict = Dictionary