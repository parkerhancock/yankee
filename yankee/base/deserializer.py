from yankee.util import is_valid, inflect, update_class
from .accessor import python_accessor

class Deserializer(object):
    class Meta:
        accessor_function = python_accessor
        infer_keys = True
        output_style = "python"

    def __init__(self, data_key=None, many=False, required=False, default=None):
        self.data_key = data_key
        self.required = required
        self.many = many
        self.default = default
        self.name = None
        self._build_meta()
        self.bind()

    def _build_meta(self):
        for c in self.__class__.mro():
            if not hasattr(c, "Meta"):
                continue
            for k in filter(lambda k: not k.startswith("_"), c.Meta.__dict__.keys()):
                if not hasattr(self.Meta, k):
                    setattr(self.Meta, k, getattr(c.Meta, k))
                
    def bind(self, name=None, parent=None):
        self.name = name
        self.parent = parent
        # Update Meta object
        if self.parent is not None:
            self.Meta = self.parent.Meta
        # Regenerate Accessor
        self.make_accessor()
        # Set Output Name
        if self.name is not None:
            self.output_name = inflect(self.name, style=self.Meta.output_style)
        return self

    def make_accessor(self):
        self.accessor = self.Meta.accessor_function(self.data_key, self.name, self.many, self.Meta)

    def load(self, obj):
        self.raw = obj
        pre_obj = self.pre_load(obj)
        loaded_obj = self.deserialize(pre_obj)
        if not is_valid(loaded_obj) and self.default is not None:
            loaded_obj = self.default
        return self.post_load(loaded_obj)

    def pre_load(self, obj):
        return obj
    
    def deserialize(self, obj):
        return self.accessor(obj)

    def post_load(self, obj):
        return obj
