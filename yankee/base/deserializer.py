from yankee.util import camelize, underscore, do_nothing


class Deserializer(object):
    data_key = None
    many = False

    class Meta:
        pass

    def __init__(self, data_key=None, required=False):
        if self.data_key is None:
            self.data_key = data_key
        self.required = required
        self.bind()

    def bind(self, name=None, parent=None):
        self.name = name
        self.parent = parent
        if self.parent is not None:
            self.Meta = parent.Meta
        self.accessor = self.make_accessor()
        return self

    def make_accessor(self):
        return do_nothing

    def load(self, obj):
        plucked_obj = self.get_obj(obj)
        loaded_obj = self.deserialize(plucked_obj)
        return self.post_load(loaded_obj)

    def deserialize(self, obj):
        return obj

    def post_load(self, obj):
        return obj

    def get_obj(self, obj):
        if self.many:
            if obj is None:
                return list()
            plucked_obj = self.accessor(obj)
            if not isinstance(plucked_obj, list):
                raise ValueError("Key Function returned single result rather than list!")
            return plucked_obj
        else:
            if obj is None:
                return None
            plucked_obj = self.accessor(obj)
            if isinstance(plucked_obj, list):
                raise ValueError("Key Function returned list of results!")
            return plucked_obj
