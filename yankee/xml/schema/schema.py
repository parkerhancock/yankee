from yankee.base import schema
from yankee.base.deserializer import Deserializer

from .fields import List
from .key import XmlMixin

class Deserializer(XmlMixin, Deserializer):
    pass

class Schema(XmlMixin, schema.Schema):
    pass


class PolymorphicSchema(XmlMixin, schema.PolymorphicSchema):
    pass

class RegexSchema(XmlMixin, schema.RegexSchema):
    pass