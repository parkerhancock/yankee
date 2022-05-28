from .deserializer import Deserializer
from sugar.util import is_valid

class Schema(Deserializer):
    class Meta():
        output_style = None

    def __init__(self, key=None, fields=None, flatten=False, prefix=False, required=False, output_style=None):
        super().__init__(key, required, output_style)
        self.Meta.output_style = output_style
        self.flatten = flatten
        self.prefix = prefix

        # Make sure that fields are grabbed from superclasses as well
        class_fields = list()
        for c in reversed(self.__class__.mro()):
            class_fields += [
                (k, v) for k, v in c.__dict__.items() if isinstance(v, Deserializer)
            ]
        self.fields = dict(class_fields)
        if isinstance(fields, dict):
            self.fields.update(fields)
        self.bind()

    def bind(self, name=None, parent=None, meta=None):
        super().bind(name, parent, meta)
        # Run bind for all contents
        for name, field in self.fields.items():
            if self.prefix:
                field.bind(f"{self.name}_{name}", self, self.Meta)
            else:
                field.bind(name, self, self.Meta)

    def deserialize(self, raw_obj) -> "Dict":
        obj = super().deserialize(raw_obj)
        output = dict()
        for field in self.fields.values():
            value = field.deserialize(obj)
            # If there is no value, don't include anything in the output dictionary
            if not is_valid(value):
                if field.required == True:
                    return dict()
                continue
            # If the value isn't a dict, or there's not flatten directive, add and continue
            if not isinstance(value, dict) or not field.flatten:
                output[field.output_name] = value
                continue
            # Merge in flattened fields
            output.update(value)
        return output

class PolymorphicSchema(Schema):    
    def bind(self, name=None, meta=None):
        super().bind(self, name, meta)
        for schema in self.schemas:
            schema.bind(name, meta)
    
    def choose_schema(self, obj):
        raise NotImplementedError("Must be implemented in subclass!")

    def deserialize(self, raw_obj) -> "Dict":
        # Get the key one time only, rather than
        # on both deserializing the selector obj
        # and the final output
        obj = super().deserialize(obj)
        schema = self.choose_schema(obj)
        return schema.deserialize(raw_obj)