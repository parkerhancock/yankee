import ujson as json
import datetime
from dataclasses import dataclass, is_dataclass, fields
from collections import abc

from .util import to_dict, DataConversion
from yankee.util import is_valid

def to_dict(obj, item_class=dict, collection_class=list, date_style="python"):
    if isinstance(obj, abc.Mapping):
        return item_class((k, to_dict(v, item_class, collection_class, date_style)) for k, v in obj.items())
    elif is_dataclass(obj):
        return to_dict(item_class(obj), item_class, collection_class, date_style)
    elif isinstance(obj, abc.Iterable) and not isinstance(obj, (str, bytes)):
        return collection_class(to_dict(i, item_class, collection_class, date_style) for i in obj)
    elif date_style == "mongo" and isinstance(obj, datetime.date):
        return datetime.datetime.combine(obj, datetime.datetime.min.time())
    elif date_style == "json" and isinstance(obj, (datetime.date, datetime.datetime)):
        return obj.isoformat()
    else:
        return obj

@dataclass
class Row(DataConversion):
    def to_dict(self):
        return to_dict(self)

    def fields(self):
        return fields(self)
    
    def __contains__(self, key):
        try:
            return getattr(self, key) is not None
        except (AttributeError, TypeError):
            return False

    def __getitem__(self, key):
        try:
            return getattr(self, key)
        except (AttributeError, TypeError):
            raise KeyError(f"'{self.__class__.__name__}' object has no attribute '{key}'")

    def get(self, key, default):
        try:
            return self[key] or default
        except KeyError:
            return default

    def items(self):
        for f in fields(self):
            yield (f.name, getattr(self, f.name))

    def values(self):
        for f in fields(self):
            yield getattr(self, f.name)
    
    def keys(self):
        for f in fields(self):
            yield f.name

    def __bool__(self):
        return not all(v is None for v in self.__dict__.values())
