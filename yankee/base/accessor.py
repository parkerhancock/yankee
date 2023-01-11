from yankee.util import camelize
from collections.abc import Sequence, Mapping

def do_nothing(obj):
    return obj

def python_accessor(data_key, name, many, meta):
    if data_key is False or (data_key is None and name is None):
        return do_nothing
    data_key = data_key or name
    key_segments = tuple(int(s) if s.isdigit() else s for s in data_key.split("."))
    def accessor_func(obj):
        result = obj
        for seg in key_segments:
            if isinstance(obj, Sequence):
                try:
                    result = result[seg]
                except IndexError:
                    result = None
            elif isinstance(result, Mapping):
                result = result.get(seg, None)
            else:
                result = getattr(result, seg, None)
        return result
    return accessor_func



