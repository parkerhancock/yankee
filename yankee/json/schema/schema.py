from yankee.base import schema

from .fields import List
from .key import JsonMixin


class Schema(JsonMixin, schema.Schema):
    pass


class PolymorphicSchema(JsonMixin, schema.PolymorphicSchema):
    pass

class RegexSchema(JsonMixin, schema.RegexSchema):
    pass