import lxml.etree as ET
from yankee.base import schema
from yankee.base.deserializer import Deserializer

from .mixin import XmlMixin

class Deserializer(XmlMixin, Deserializer):
    pass

class Schema(XmlMixin, schema.Schema):
    def load(self, obj):
        if isinstance(obj, (ET._Element, ET._ElementTree)):
            return super().load(obj)
        elif isinstance(obj, str):
            return super().load(ET.fromstring(obj.encode()))
        elif isinstance(obj, bytes):
            return super().load(ET.fromstring(obj))


class PolymorphicSchema(XmlMixin, schema.PolymorphicSchema):
    pass

class RegexSchema(XmlMixin, schema.RegexSchema):
    pass

class ZipSchema(XmlMixin, schema.ZipSchema):
    pass