from .accessor import json_accessor

class JsonMixin(object):
    list_field = "yankee.json.schema.fields.List"

    class Meta():
        accessor_function = json_accessor
        infer_keys = True
