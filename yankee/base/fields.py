from __future__ import annotations
import typing
import datetime
import re
import importlib
import warnings

from dateutil.parser import parse as parse_dt, isoparse

from yankee.util import AttrDict, clean_whitespace, is_valid, import_class

from yankee.data.collection import ListCollection
from .deserializer import Deserializer
from .schema import Schema
from functools import partial


class Field(Deserializer):
    """The basic field - performs no type casting"""
    output_type = typing.Any
    def __init__(self, *args, default=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.default = default
    
    def load(self, obj):
        result = super().load(obj)
        return result if is_valid(result) else self.default

class String(Field):
    """String Field

    Always outputs a string value, or None

    Args:
        formatter (Callable): a callable for formatting the resulting string. Defaults to a newline-preserving whitespace cleaner
        null_value (str): a string value to indicate that it should be None. Some data sources use a hyphen or other symbol rather than empty value
    """
    output_type = str
    def __init__(self, *args, formatter=None, null_value=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.formatter = formatter or partial(clean_whitespace, preserve_newlines=True)
        self.null_value = null_value

    def deserialize(self, elem) -> "Optional[str]":
        elem = super().deserialize(elem)
        if elem is None or elem == "" or elem == self.null_value:
            return None
        else:
            return self.formatter(self.to_string(elem)) if self.formatter else self.to_string(elem)

    def to_string(self, elem): # Abstracted out since XML requires a function call
        return str(elem)


class DateTime(String):
    """DateTime Field
    
    Always outputs a datetime.datetime value. The initial value retrieved should be a string, which is then parsed as an isoformatted date. If that parsing fails, it uses `dateutil.parser.parse` to attempt to retrieve a datetime.
    
    Args:
        dt_format (str): a formatting string from datetime.datetime.strptime to use
        dt_converter (callable): a custom function to parse a date, overriding the default
    """
    output_type = datetime.datetime
    def __init__(self, *args, dt_format=None, dt_converter=False, **kwargs):
        super().__init__(*args, **kwargs)
        if dt_converter:
            self.parse_date = dt_converter
        elif dt_format:
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
    """Date Field

    Always outputs a datetime.date value. Uses the same args as DateTime
    """
    output_type = datetime.date
    def deserialize(self, elem) -> "Optional[datetime.date]":
        date_time = super().deserialize(elem)
        return date_time.date() if date_time else None


class Boolean(String):
    """Boolean Field
    
    Always outputs a boolean value (True, or False)

    Args:
        true_value (str): a custom string value that should be considered truthy
        true_func (Callable): a custom function that, when executed on the result, should return True or False
        case_sensitive (str): if a true_value is provided, whether it should be considered case sensitive
        allow_none (str): if the data key doesn't find a match, and this is true, then it will return None rather than False
    """
    output_type = bool
    def __init__(
        self, *args, true_value="true", true_func=None, case_sensitive=False, allow_none=True, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.true_value = true_value
        self.case_sensitive = case_sensitive
        self.allow_none = allow_none
        self.true_func = true_func
        if not self.case_sensitive:
            self.true_value = self.true_value.lower()

    def deserialize(self, elem) -> "Optional[bool]":
        string = super(Boolean, self).deserialize(elem)
        if string is None or string == '':
            return None if self.allow_none else False
        if callable(self.true_func):
            return self.true_func(string)
        if not self.case_sensitive:
            string = string.lower()
        return string == self.true_value


class Float(String):
    """Float Field

    Always outputs a float value
    """
    output_type = float
    def deserialize(self, elem) -> "Optional[float]":
        string = super(Float, self).deserialize(elem)
        return float(string) if string is not None else None


class Integer(String):
    """Float Field

    Always outputs an integer value. If the value is a float, the result will be the result of calling `int` on the value.
    """
    output_type = int
    def deserialize(self, elem) -> "Optional[int]":
        string = super(Integer, self).deserialize(elem)
        return int(string) if string is not None else None


class Exists(Field):
    """Exists Field
    
    Outputs true if the data item is present, else false
    """
    output_type = bool
    def deserialize(self, elem) -> bool:
        obj = super(Exists, self).deserialize(elem)
        return obj is not None


class Const(Field):
    """Constant Field
    
    Always outputs the provided constant value

    Args:
        const (any): The constant value to return
    """
    def __init__(self, const, output_type=None, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        self.const = const
        if output_type is None:
            warnings.warn(f"Constant has unassigned output type - cannot infer output schema without constant type information")
        self.output_type = output_type

    def deserialize(self, elem) -> "Any":
        return self.const
    

# Multiple Value Fields
    
class Nested(Schema):
    output_type = dict
    def __init__(self, schema, *args, **kwargs):
        self._schema = schema
        self._args = args
        self._kwargs = kwargs

    # Deserialize Methods
    def bind(self, name=None, parent=None, meta=None):
        super().bind(name=name, parent=parent)
        if isinstance(self._schema, str):
            *module, _schema = self._schema.split(".")
            module = ".".join(module) or parent.__module__
            schema_class = getattr(importlib.import_module(module), _schema)
            self._schema = schema_class(*self._args, **self._kwargs)
        self._schema.bind(name, parent, meta)

    def make_accessor(self, *args, **kwargs):
        if isinstance(self._schema, str):
            return
        return self._schema.make_accessor(*args, **kwargs)

    def load(self, obj):
        return self._schema.load(obj)

class List(Field):
    output_type = list
    def __init__(self, item_schema, data_key=None, **kwargs):
        kwargs['many'] = True
        self.item_schema = item_schema
        if callable(self.item_schema):
            self.item_schema = item_schema()
        super().__init__(data_key, **kwargs)

    def bind(self, name=None, schema=None, meta=None):
        super().bind(name, schema, meta)
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

    def load(self, obj):
        obj = super().load(obj)
        if not obj:
            return ListCollection()
        obj_gen = (self.item_schema.load(i) for i in obj)
        return ListCollection(o for o in obj_gen if is_valid(o))

class Dictionary(List):
    output_type = dict
    """Converts a list of items into a dictionary based on
    the key and value fields passed to it.
    """
    
    def __init__(self, data_key, key:Field, value:Field, **kwargs):
        self.key = key
        self.value = value
        return super().__init__(Field(), data_key, **kwargs)
    
    def load(self, obj):
        obj = self.deserialize(obj)
        if not obj:
            return AttrDict()
        return AttrDict((self.key.load(i), self.value.load(i)) for i in obj)

# String Parsing Fields

class DelimitedString(String):
    output_type = list
    def __init__(self, item_schema, data_key=None, delimeter=",", **kwargs):
        self.item_schema = item_schema
        if not isinstance(delimeter, re.Pattern):
            delimeter = re.compile(delimeter)
        self.delimeter = delimeter
        if callable(self.item_schema):
            self.item_schema = item_schema()
        super().__init__(data_key=data_key, **kwargs)

    def bind(self, name=None, schema=None, meta=None):
        super().bind(name, schema, meta=None)
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
    output_type = str

    def bind(self, name=None, parent=None, meta=None):
        super().bind(name, parent)
        for field in self.fields.values():
            field.output_name = field.name
        self.__model__ = self.make_dataclass()

    def load(self, obj):
        loaded_obj = super().load(obj)
        return self.combine_func(loaded_obj)

    def combine_func(self, obj):
        raise NotImplementedError("Must be implemented in subclass")

    def get_model(self):
        return AttrDict


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