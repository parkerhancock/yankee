from .key import JsonMixin
from gelatin_extract.base import schema

class Schema(JsonMixin, schema.Schema):
    pass

class PolymorphicSchema(JsonMixin, schema.PolymorphicSchema):
    pass