from .key import JsonMixin
from yankee.base import schema

class Schema(JsonMixin, schema.Schema):
    pass

class PolymorphicSchema(JsonMixin, schema.PolymorphicSchema):
    pass