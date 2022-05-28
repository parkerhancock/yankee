from .key import JsonMixin
from sugar.base import schema

class Schema(JsonMixin, schema.Schema):
    pass

class PolymorphicSchema(JsonMixin, schema.PolymorphicSchema):
    pass