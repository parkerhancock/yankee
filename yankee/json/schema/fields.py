import lxml.etree as ET
from yankee.base import fields
from yankee.util import clean_whitespace

from .mixin import JsonMixin


class Field(JsonMixin, fields.Field):
    pass


class String(JsonMixin, fields.String):
    pass


class DateTime(JsonMixin, fields.DateTime):
    pass


class Date(JsonMixin, fields.Date):
    pass


class Boolean(JsonMixin, fields.Boolean):
    pass


class Float(JsonMixin, fields.Float):
    pass


class Integer(JsonMixin, fields.Integer):
    pass


class Exists(JsonMixin, fields.Exists):
    pass


class Const(JsonMixin, fields.Const):
    pass


class List(JsonMixin, fields.List):
    pass

class Dict(JsonMixin, fields.Dict):
    pass

class Combine(JsonMixin, fields.Combine):
    pass

class Alternative(JsonMixin, fields.Alternative):
    pass

class DelimitedString(JsonMixin, fields.DelimitedString):
    pass

class Nested(JsonMixin, fields.Nested):
    pass

class TailField(fields.Field):
    """Field to retreive tail text"""

    def load(self, obj):
        return super().load(obj)

    def deserialize(self, obj):
        return clean_whitespace(super().deserialize(obj).tail)

# Aliases
Str = String
DT = DateTime
Bool = Boolean
Int = Integer
Alt = Alternative
