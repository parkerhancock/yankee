from .key import XmlMixin
from .fields import List
from yankee.base import schema

class Schema(XmlMixin, schema.Schema):
    pass

class PolymorphicSchema(XmlMixin, schema.PolymorphicSchema):
    pass

class ZipSchema(XmlMixin, schema.ZipSchema):
    _list_field = List