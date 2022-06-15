from yankee.util import do_nothing
from collections.abc import Mapping, Sequence

class DefaultPath():
    def __init__(self, data_key):
        self.key = data_key.split(".")

    def __call__(self, obj):
        try:
            result = obj
            for k in self.key:
                if isinstance(result, Sequence) and k.isdigit():
                    result = result[int(k)]
                elif isinstance(result, Mapping):
                    result = result[k]
                else:
                    result = getattr(result, k)
            return result
        except (AttributeError, KeyError, IndexError):
            return None



class Deserializer(object):
    many = False

    class Meta:
        pass

    def __init__(self, data_key=None, required=False):
        self.data_key = data_key
        self.required = required
        self.bind()

    def bind(self, name=None, parent=None):
        self.name = name
        self.parent = parent
        if self.parent is not None:
            self.Meta = parent.Meta
        self.accessor = self.make_accessor()
        return self

    def make_accessor(self):
        if self.data_key == False:
            return do_nothing
        key = self.data_key or self.name
        if key is None:
            return do_nothing
        return DefaultPath(key)

    def load(self, obj):
        pre_obj = self.pre_load(obj)
        plucked_obj = self.get_obj(pre_obj)
        loaded_obj = self.deserialize(plucked_obj)
        return self.post_load(loaded_obj)

    def pre_load(self, obj):
        return obj
    
    def deserialize(self, obj):
        return obj

    def post_load(self, obj):
        return obj

    def get_obj(self, obj):
        if self.many:
            if obj is None:
                return list()
            plucked_obj = self.accessor(obj)
            if not isinstance(plucked_obj, list):
                raise ValueError("Key Function returned single result rather than list!")
            return plucked_obj
        else:
            if obj is None:
                return None
            plucked_obj = self.accessor(obj)
            if isinstance(plucked_obj, list):
                raise ValueError("Key Function returned list of results!")
            return plucked_obj
