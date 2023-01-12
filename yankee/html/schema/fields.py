import lxml.etree as ET
from yankee.base import fields
from yankee.util import clean_whitespace

from .mixin import HtmlMixin


class Field(HtmlMixin, fields.Field):
    pass


class String(HtmlMixin, fields.String):
    pass


class DateTime(HtmlMixin, fields.DateTime):
    pass


class Date(HtmlMixin, fields.Date):
    pass


class Boolean(HtmlMixin, fields.Boolean):
    pass


class Float(HtmlMixin, fields.Float):
    pass


class Integer(HtmlMixin, fields.Integer):
    pass


class Exists(HtmlMixin, fields.Exists):
    pass


class Const(HtmlMixin, fields.Const):
    pass


class List(HtmlMixin, fields.List):
    pass

class Dict(HtmlMixin, fields.Dict):
    pass

class Combine(HtmlMixin, fields.Combine):
    pass

class Alternative(HtmlMixin, fields.Alternative):
    pass

class DelimitedString(HtmlMixin, fields.DelimitedString):
    pass

class Nested(HtmlMixin, fields.Nested):
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
