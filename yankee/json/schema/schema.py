from yankee.base import schema
import ujson as json
from .mixin import JsonMixin
from .fields import List

class Schema(JsonMixin, schema.Schema):
    def load(self, obj):
        if self.name is not None or isinstance(obj, dict):
            return super().load(obj)
        elif isinstance(obj, str):
            return super().load(json.loads(obj))
        elif isinstance(obj, bytes):
            return super().load(json.loads(obj.decode()))

    def load_batch(self, obj):
        if self.name is not None or isinstance(obj, list):
            return super().load_batch(obj)
        elif isinstance(obj, str):
            return super().load_batch(json.loads(obj))
        elif isinstance(obj, bytes):
            return super().load_batch(json.loads(obj.decode()))

class PolymorphicSchema(JsonMixin, schema.PolymorphicSchema):
    pass

class RegexSchema(JsonMixin, schema.RegexSchema):
    pass

class ZipSchema(JsonMixin, schema.ZipSchema):
    pass