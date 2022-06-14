from copy import deepcopy
from yankee.util import is_valid

from .deserializer import Deserializer


class Schema(Deserializer):
    class Meta:
        output_style = None

    def __init__(
        self,
        data_key=None,
        flatten=False,
        prefix=False,
        required=False,
        output_style=None,
    ):
        super().__init__(data_key, required, output_style)
        self.Meta.output_style = output_style
        self.flatten = flatten
        self.prefix = prefix
        self.bind()

    def bind(self, name=None, parent=None):
        super().bind(name, parent)
        # Make sure that fields are grabbed from superclasses as well
        class_fields = list()
        for c in reversed(self.__class__.mro()):
            class_fields += [
                (k, v) for k, v in c.__dict__.items() if isinstance(v, Deserializer)
            ]
        self.fields = dict(class_fields)
        for name, field in self.fields.items():
            if self.prefix:
                field.bind(f"{self.name}_{name}", self)
            else:
                field.bind(name, self)

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


class ZipSchema(Schema):
    _list_field = None
    """Sometimes data is provided as a bunch of arrays, like:
    {
        "name": ["Peter", "Parker"],
        "age": [15, 25],
    }
    and we want to build out complete records from this data.
    This field performs that step:
    """

    def bind(self, name=None, parent=None):
        super().bind(name=name, parent=parent)
        from yankee.xml import Deserializer as XmlDeserializer
        if not hasattr(self, "_keys"):
            self._keys = list()
            for f in self.fields.values():
                generic_f = XmlDeserializer(f.data_key, f.required)
                generic_f.bind(f.name, parent)
                self._keys.append(generic_f)

    def lists_to_records(self, obj):
        keys = tuple(obj.keys())
        values = tuple(obj.values())
        return [dict(zip(keys, v)) for v in zip(*values)]

    def deserialize(self, raw_obj) -> "Dict":
        elements = [f.deserialize(raw_obj) for f in self._keys]
        import lxml.etree as ET
        docs = list(map(list, zip(*elements)))

        obj = super().deserialize(raw_obj)
        return self.lists_to_records(obj)
