from yankee.base import schema
import ujson as json
from .mixin import JsonMixin


class Schema(JsonMixin, schema.Schema):
    def load(self, obj):
        if isinstance(obj, dict):
            return super().load(obj)
        elif isinstance(obj, str):
            return super().load(json.loads(obj))
        elif isinstance(obj, bytes):
            return super().load(json.loads(obj.decode()))

class PolymorphicSchema(JsonMixin, schema.PolymorphicSchema):
    pass

class RegexSchema(JsonMixin, schema.RegexSchema):
    pass

class ZipSchema(JsonMixin, schema.ZipSchema):
    pass