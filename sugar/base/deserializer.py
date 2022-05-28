from sugar.util import underscore, camelize
import logging

def do_nothing(obj):
    return obj

class Deserializer(object):
    raw_key = None
    many = False

    class Meta():
        output_style = None

    def __init__(self, key=None, required=False, output_style=None):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.raw_key = key or self.raw_key
        self.required = required
        self.output_style = output_style

    def bind(self, name=None, parent=None, meta=None):
        self.name = name
        self.parent = parent
        self.Meta = meta
        self.key = self.generate_key()
        self.output_name = self.generate_output_name()
        self.key_func = self.create_key_func()

    def generate_output_name(self):
        if self.name and self.Meta:
            if self.Meta.output_style == "json":
                return camelize(self.name)
            elif self.Meta.output_style == "python":
                return underscore(self.name)
        elif self.name:
                return self.name
        else:
            return underscore(self.__class__.__name__)

    def generate_key(self):
        return self.raw_key or self.name

    def create_key_func(self):
        return do_nothing

    def deserialize(self, obj):
        self.raw_obj = obj
        if self.many:
            if obj is None:
                return list()
            return self.key_func(obj)
        else:
            if obj is None:
                return None
            plucked_obj = self.key_func(obj)
            if isinstance(plucked_obj, list):
                if len(plucked_obj) > 1:
                    raise ValueError("Key Function returned multiple results!")
                elif not plucked_obj:
                    return None
                else:
                    return plucked_obj[0]
            return plucked_obj


