import datetime
from collections import abc
from yankee.util import camelize, underscore, AttrDict


def jsonify(obj):
    if isinstance(obj, abc.Mapping):
        return AttrDict((camelize(k), jsonify(v)) for k, v in obj.items())
    elif isinstance(obj, abc.Sequence) and not isinstance(obj, (str, bytes)):
        return [jsonify(i) for i in obj]
    elif isinstance(obj, datetime.datetime):
        return obj.isoformat()
    elif isinstance(obj, datetime.date):
        return datetime.datetime.combine(obj, datetime.datetime.min.time()).isoformat()
    else:
        return obj

def pythonify(obj):
    if isinstance(obj, abc.Mapping):
        return AttrDict((underscore(k), pythonify(v)) for k, v in obj.items())
    elif isinstance(obj, abc.Sequence) and not isinstance(obj, (str, bytes)):
        return [pythonify(i) for i in obj]
    else:
        return obj