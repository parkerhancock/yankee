from collections.abc import Mapping, Sequence


def do_nothing(obj):
    return obj


class JsonPath(object):
    def __init__(self, key, many=False):
        self.key = key.split(".")
        self.many = many

    def __call__(self, obj):
        try:
            for k in self.key:
                if isinstance(obj, Mapping):
                    obj = obj[k]
                elif isinstance(obj, Sequence) and k.isdigit():
                    obj = obj[int(k)]
                elif isinstance(obj, Sequence):
                    obj = [o[k] for o in obj]
                else:
                    raise IndexError(f"Cannot get key {k} from {obj}")
            if not self.many and isinstance(obj, list):
                raise ValueError(
                    f"Expected {'.'.join(self.key)} to produce single value, got many: {obj}"
                )
            elif self.many and not isinstance(obj, list):
                raise ValueError(
                    f"Expected {'.'.join(self.key)} to produce many values, got one: {obj}"
                )
            return obj
        except (IndexError, KeyError):
            if self.many:
                return list()
            return None


class JsonMixin(object):
    def make_accessor(self):
        data_key = self.data_key or self.name
        if data_key is None:
            return do_nothing
        return JsonPath(data_key, many=self.many)
