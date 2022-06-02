from yankee.base import schema

from .fields import List
from .key import JsonMixin


class Schema(JsonMixin, schema.Schema):
    pass


class PolymorphicSchema(JsonMixin, schema.PolymorphicSchema):
    pass


class ZipSchema(JsonMixin, schema.ZipSchema):
    _list_field = List
