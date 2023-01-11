from collections.abc import Sequence
from yankee.util import camelize
from yankee.base.accessor import do_nothing


def json_accessor(data_key, name, many, meta):
    if data_key is False or (data_key is None and name is None):
        return do_nothing
    elif data_key is None:
        data_key = camelize(name)
    key_segments = tuple(int(s) if s.isdigit() else s for s in data_key.split("."))
    def accessor_func(obj):
        result = obj
        for seg in key_segments:
            if isinstance(obj, Sequence):
                try:
                    result = result[int(seg)]
                except IndexError:
                    result = None
            else:
                result = result.get(seg, None)
        return result
    return accessor_func