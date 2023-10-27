import datetime
import json
from typing import *
import dataclasses
from collections import abc


class JsonEncoder(json.JSONEncoder):
    def default(self, o: "Any") -> "Any":
        if isinstance(o, (datetime.date, datetime.datetime)):
            return o.isoformat()
        elif hasattr(o, "to_dict"):
            return o.to_dict()
        return json.JSONEncoder.default(self, o)

def to_dict(obj, item_class=dict, collection_class=list, date_style="python"):
    # print(f"Obj is {obj}")
    if isinstance(obj, abc.Mapping):
        # print(f"Casting as Mapping with class {item_class}")
        return item_class((k, to_dict(v, item_class, collection_class, date_style)) for k, v in obj.items())
    elif dataclasses.is_dataclass(obj):
        # print("Converting Dataclass")
        return to_dict(item_class(obj), item_class, collection_class, date_style)
    elif isinstance(obj, abc.Iterable) and not isinstance(obj, (str, bytes)):
        # print(f"Casting as Collection with {collection_class}")
        return collection_class(to_dict(i, item_class, collection_class, date_style) for i in obj)
    elif date_style == "mongo" and isinstance(obj, datetime.date):
        return datetime.datetime.combine(obj, datetime.datetime.min.time())
    elif date_style == "json" and isinstance(obj, (datetime.datetime, datetime.date)):
        return obj.isoformat()
    else:
        # print("No cast - passing through")
        return obj
    
async def ato_dict(obj, item_class=dict, collection_class=list, date_style="python"):
    if isinstance(obj, abc.AsyncIterable):
        obj = [o async for o in obj]
    return to_dict(obj, item_class, collection_class, date_style)


def resolve_list(item, key):
    item_list = resolve(item, key)

    if item_list is None:
        return []

    if isinstance(item_list, list):
        return item_list

    return [item_list]

def resolve_attribute(obj, key):
    if isinstance(obj, abc.Mapping):
        obj = obj[key]
    else:
        obj = getattr(obj, key)
    if callable(obj):
        obj = obj()
    return obj


def resolve(item, key):
    if key is None:
        return item
    accessors = key.split(".")
    try:
        for accessor in accessors:
            if isinstance(item, abc.Sequence) and accessor.isdigit():
                item = item[int(accessor)]
            elif isinstance(item, abc.Sequence) and not accessor.isdigit():
                item = [resolve_attribute(i, accessor) for i in item]
            else:
                item = resolve_attribute(item, accessor)
    except Exception as e:
        return None
    return item

class DataConversion():
    def to_mongo(self):
        """Convert object to a Python dictionary with datetime.dates converted to datetime.datetimes for MongoDB compatibility"""
        return to_dict(self, date_style="mongo")

    def to_pandas(self):
        """Convert object to Pandas Series"""
        import pandas as pd

        return pd.Series(to_dict(self))

    def to_json(self, *args, **kwargs):
        """Convert object to a JSON string"""
        return json.dumps(to_dict(self, date_style="json"), *args, **kwargs)

    def to_dict(self, item_class=dict, collection_class=list, date_style="python"):
        """Convert object to simple Python dictionary"""
        return to_dict(self, item_class=item_class, collection_class=collection_class, date_style=date_style)