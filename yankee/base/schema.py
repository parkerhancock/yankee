from yankee.util import camelize, underscore, is_valid

from .deserializer import Deserializer



def inflect(string, style=None):
    try:
        if style is None:
            return string
        elif style == "json":
            return camelize(string)
        elif style == "python":
            return underscore(string)
    except Exception:
        return None

class Schema(Deserializer):
    class Meta:
        output_style = "python"

    def __init__(
        self,
        data_key=None,
        flatten=False,
        prefix=False,
        required=False,
    ):
        self.flatten = flatten
        self.prefix = prefix
        super().__init__(data_key, required)

    def bind(self, name=None, parent=None):
        super().bind(name, parent)
        # Make sure that fields are grabbed from superclasses as well
        class_fields = list()
        for c in reversed(self.__class__.mro()):
            class_fields += [
                (k, v) for k, v in c.__dict__.items() if isinstance(v, Deserializer)
            ]
        fields = dict(class_fields)
        for name, field in fields.items():
            field.bind(name, self)
        self.fields = {self.get_output_name(k): v for k, v in fields.items()}

    def get_output_name(self, name):
        output_style = getattr(self.Meta, "output_style", None)
        if output_style == None:
            return name
        elif output_style == "json":
            name = camelize(name)
            if self.prefix:
                return camelize(self.name) + name[0].upper() + name[1:]
            return name
        elif output_style == "python":
            name = underscore(name)
            if self.prefix:
                return underscore(self.name) + "_" + name
            return name

    def deserialize(self, obj) -> "Dict":
        output = dict()
        for key, field in self.fields.items():
            value = field.load(obj)
            # If there is no value, don't include anything in the output dictionary
            if not is_valid(value):
                if field.required == True:
                    return dict()
                continue
            # If the value isn't a dict, or there's not flatten directive, add and continue
            if not isinstance(value, dict) or not field.flatten:
                output[key] = value
                continue
            # Merge in flattened fields
            output.update(value)
        return output


class PolymorphicSchema(Schema):
    def bind(self, name=None):
        super().bind(self, name)
        for schema in self.schemas:
            schema.bind(name)

    def choose_schema(self, obj):
        raise NotImplementedError("Must be implemented in subclass!")

    def deserialize(self, raw_obj) -> "Dict":
        # Get the key one time only, rather than
        # on both deserializing the selector obj
        # and the final output
        obj = super().deserialize(obj)
        schema = self.choose_schema(obj)
        return schema.deserialize(raw_obj)

