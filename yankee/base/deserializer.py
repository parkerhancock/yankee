from yankee.util import camelize


def do_nothing(obj):
    return obj


class Deserializer(object):
    data_key = None
    many = False

    def __init__(self, data_key=None, required=False, output_style=None):
        if self.data_key is None:
            self.data_key = data_key
        self.required = required
        self.output_style = output_style

    def bind(self, name=None, parent=None):
        self.name = name
        self.parent = parent
        self.output_name = camelize(self.name) if self.name else None
        if self.data_key == False:
            self.accessor = do_nothing
        else:
            self.accessor = self.make_accessor()

    def make_accessor(self):
        return do_nothing

    def post_load(self, output_data, **kwargs):
        return output_data

    def deserialize(self, obj):
        if self.many:
            if obj is None:
                return list()
            return self.accessor(obj)
        else:
            if obj is None:
                return None
            plucked_obj = self.accessor(obj)
            if isinstance(plucked_obj, list):
                if len(plucked_obj) > 1:
                    raise ValueError("Key Function returned multiple results!")
                elif not plucked_obj:
                    return self.post_load(None)
                else:
                    return self.post_load(plucked_obj[0])
            return self.post_load(plucked_obj)
