import lxml.html as ET
from lxml.etree import _Element
from yankee.base import schema
from yankee.base.deserializer import Deserializer

from .mixin import HtmlMixin

class Deserializer(HtmlMixin, Deserializer):
    pass

class Schema(HtmlMixin, schema.Schema):
    def load(self, obj):
        if isinstance(obj, _Element):
            return super().load(obj)
        elif isinstance(obj, str):
            return super().load(ET.fromstring(obj.encode()))
        elif isinstance(obj, bytes):
            return super().load(ET.fromstring(obj))


class PolymorphicSchema(HtmlMixin, schema.PolymorphicSchema):
    pass


class RegexSchema(HtmlMixin, schema.RegexSchema):
    pass

class ZipSchema(HtmlMixin, schema.ZipSchema):
    pass