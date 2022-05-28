from .key import XmlMixin
from sugar.base import schema

class Schema(XmlMixin, schema.Schema):
    pass

class PolymorphicSchema(XmlMixin, schema.PolymorphicSchema):
    pass