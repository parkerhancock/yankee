from yankee.base.deserializer import DefaultAccessor
from yankee.util import do_nothing, camelize

class JsonMixin(object):
    def make_accessor(self, data_key, name, many, filter):
        if self.data_key == False:
            return do_nothing
        data_key = self.data_key or self.name
        if data_key is None:
            return do_nothing
        return DefaultAccessor(camelize(data_key), many=self.many, filter=self.filter)
