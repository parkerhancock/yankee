from .key import XmlMixin
from gelatin_extract.base import schema

class Schema(XmlMixin, schema.Schema):
    pass

class PolymorphicSchema(XmlMixin, schema.PolymorphicSchema):
    pass