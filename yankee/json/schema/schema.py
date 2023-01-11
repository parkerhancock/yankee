from yankee.base import schema

from .mixin import JsonMixin


class Schema(JsonMixin, schema.Schema):
    pass

class PolymorphicSchema(JsonMixin, schema.PolymorphicSchema):
    pass

class RegexSchema(JsonMixin, schema.RegexSchema):
    pass

class ZipSchema(JsonMixin, schema.ZipSchema):
    pass