from collections.abc import Sequence
from yankee.util import camelize
from yankee.base.accessor import do_nothing
import jsonpath_ng


def json_accessor(data_key, name, many, meta):
    # Handle JSONPath objects passed as data keys
    if isinstance(data_key, jsonpath_ng.JSONPath):
        def accessor_func(obj):
            result = [match.value for match in data_key.find(obj)]
            try:
                return result if many else result[0]
            except IndexError:
                return None
        return accessor_func
    # Handle no data key
    if data_key is False or (data_key is None and name is None):
        return do_nothing
    # Handle implicit data keys
    elif data_key is None and meta.infer_keys:
        data_key = camelize(name)
    key_segments = tuple(int(s) if s.isdigit() else s for s in data_key.split("."))
    def accessor_func(obj):
        result = obj
        for seg in key_segments:
            if isinstance(result, Sequence) and not isinstance(result, str):
                try:
                    result = result[int(seg)]
                except IndexError:
                    result = None
            elif result is None:
                return None
            else:
                result = result.get(seg, None)
        return result
    return accessor_func