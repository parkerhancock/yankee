from yankee.util import do_nothing, update_class
from collections.abc import Mapping, Sequence


class JsonPath():
    def __init__(self, data_key=None):
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


class DefaultAccessor():
    def __init__(self, data_key=None, many=False, filter=None):
        self.data_key = data_key
        self.many = many
        self.filter = filter
        self.path_obj = self.make_path_obj()

    def make_path_obj(self):
        return JsonPath(self.data_key) if self.data_key is not None else do_nothing

    def __call__(self, obj, *args, **kwargs):
        if obj is None:
            return None
        result = self.path_obj(obj, *args, **kwargs)
        result = self.apply_filter(result)
        if not self.many and isinstance(result, list):
            if len(result) == 1:
                result = result[0]
            elif len(result) == 0:
                result = None
        return self.raise_exceptions(result)
        
    def apply_filter(self, result):
        if self.filter is None:
            return result
        if isinstance(result, list):
            return [r for r in result if self.filter(r)]
        else:
            return result if self.filter(result) else None

    def raise_exceptions(self, result):
        if self.many and not isinstance(result, list):
            raise ValueError("Expected many results, got one!")
        elif not self.many and isinstance(result, list):
            raise ValueError("Expected one result, got many!")
        return result

    def __getstate__(self):
        state = self.__dict__.copy()
        del state['path_obj']
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self.path_obj = self.make_path_obj()


class Deserializer(object):
    class Meta:
        pass

    def __init__(self, data_key=None, many=False, required=False, filter=None):
        self.data_key = data_key
        self.required = required
        self.filter = filter
        self.many = many
        self.bind()

    def bind(self, name=None, parent=None):
        self.name = name
        self.parent = parent
        if self.parent is not None:
            update_class(self.Meta, parent.Meta)
        self.accessor = self.make_accessor(self.data_key, self.name, self.many, self.filter)
        return self

    def make_accessor(self, data_key, name, many, filter):
        if data_key == False:
            return do_nothing
        key = data_key or name
        return DefaultAccessor(key, many=many, filter=filter)

    def load(self, obj):
        pre_obj = self.pre_load(obj)
        plucked_obj = self.get_obj(pre_obj)
        loaded_obj = self.deserialize(plucked_obj)
        return self.post_load(loaded_obj)

    def pre_load(self, obj):
        return obj
    
    def deserialize(self, obj):
        if obj is None and self.required:
            raise ValueError(
                f"Field {self.name} is required! Key {self.key} not found in {obj}"
            )
        return obj

    def post_load(self, obj):
        return obj

    def get_obj(self, obj):
        return self.accessor(obj)
