from yankee.base import schema

from .fields import List
from .key import XmlMixin


class Schema(XmlMixin, schema.Schema):
    pass


class PolymorphicSchema(XmlMixin, schema.PolymorphicSchema):
    pass


class ZipSchema(XmlMixin, schema.ZipSchema):
    _list_field = List
