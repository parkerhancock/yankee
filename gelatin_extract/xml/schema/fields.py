from .key import XmlMixin

from gelatin_extract.base import fields

class Field(XmlMixin, fields.Field):
    pass

class String(XmlMixin, fields.String):
    pass        

class DateTime(XmlMixin, fields.DateTime):
    pass

class Date(XmlMixin, fields.Date):
    pass

class Boolean(XmlMixin, fields.Boolean):
    pass

class Float(XmlMixin, fields.Float):
    pass

class Integer(XmlMixin, fields.Integer):
    pass

class Exists(XmlMixin, fields.Exists):
    pass

class Const(XmlMixin, fields.Const):
    pass

class List(XmlMixin, fields.List):
    pass

class Combine(XmlMixin, fields.Combine):
    pass

class Alternative(XmlMixin, fields.Alternative):
    pass

#Aliases
Str = String
DT = DateTime
Bool = Boolean
Int = Integer
Alt = Alternative