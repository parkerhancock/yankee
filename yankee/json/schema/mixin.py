from .accessor import json_accessor

class JsonMixin(object):
    class Meta():
        accessor_function = json_accessor
        infer_keys = True
