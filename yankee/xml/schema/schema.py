from .key import XmlMixin
from yankee.base import schema

class Schema(XmlMixin, schema.Schema):
    pass

class PolymorphicSchema(XmlMixin, schema.PolymorphicSchema):
    pass