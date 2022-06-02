from .key import JsonMixin
from .fields import List
from yankee.base import schema

class Schema(JsonMixin, schema.Schema):
    pass

class PolymorphicSchema(JsonMixin, schema.PolymorphicSchema):
    pass

class ZipSchema(JsonMixin, schema.ZipSchema):
    _list_field = List