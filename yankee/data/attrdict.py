import ujson as json
from .util import DataConversion

class AttrDict(dict, DataConversion):    
    def __getattr__(self,  name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)
    
    def __setattr__(self, name, value):
        self[name] = value
    
    @classmethod
    def convert(cls, obj):
        if isinstance(obj, dict):
            return cls((k, cls.convert(v)) for k, v in obj.items())
        elif isinstance(obj, list):
            return list(cls.convert(i) for i in obj)
        else:
            return obj