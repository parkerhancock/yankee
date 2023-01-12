import re
import dataclasses as dc
import importlib
from yankee.util import is_valid, AttrDict, clean_whitespace, unzip_records

from yankee.data.row import Row
from .deserializer import Deserializer
from yankee.data.collection import ListCollection, Collection


class Schema(Deserializer):
    output_type=dict
    def __init__(
        self,
        *args,
        flatten=False,
        prefix=False,
        **kwargs
    ):
        self.flatten = flatten
        self.prefix = prefix
        super().__init__(*args, **kwargs)
        self.bind()

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
            if self.prefix:
                field.bind(f"{self.name}_{name}", self)
            else:
                field.bind(name, self)
        self.fields = fields
        self.get_model()

    def get_model(self):
        if hasattr(self, "__model__"):
            if isinstance(self.__model__, str):
                *module, _model = self.__model__.rsplit(".", 1)
                if not module:
                    module = self.__class__.__module__.rsplit(".", 1)[0] + ".model"
                    self.__model__ = getattr(importlib.import_module(module), _model)
        else:
            self.__model__ = self.make_dataclass()
        

    def deserialize(self, obj) -> "Dict":
        output = dict()
        obj = self.accessor(obj)
        for key, field in self.fields.items():
            value = field.load(obj)
            # If there is no value, don't include anything in the output dictionary
            if not is_valid(value):
                continue
            # If the value isn't a dict, or there's not flatten directive, add and continue
            if not isinstance(value, dict) or not getattr(field, "flatten", False):
                output[field.output_name] = value
                continue
            # Merge in flattened fields
            output.update(value)
        return self.__model__(**output)

    def make_field(self, t):
        if t == list:
            return dc.field(default_factory=ListCollection)
        else:
            return dc.field(default=None)

    def make_dataclass(self):
        fields = list(
            (f.output_name, f.output_type, self.make_field(f.output_type))
            for f in self.fields.values()
            )
        dataclass = dc.make_dataclass(
            cls_name=self.__class__.__name__.replace("Schema", ""),
            fields=fields,
            bases=(Row,)
        )
        return dataclass

    def load_batch(self, objs):
        return Collection(self.load(o) for o in objs)


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

class RegexSchema(Schema):
    """
    This schema type allows for using a regex to pull data
    out of a string, and then treat it like a schema
    """
    __regex__ = None
    
    def __init__(self, *args, **kwargs):
        self._regex = re.compile(self.__regex__)
        super().__init__(*args, **kwargs)
        
    def deserialize(self, obj):
        obj = self.accessor(obj)
        if obj is None:
            return None
        text = clean_whitespace(self.to_string(obj))
        match = self._regex.search(text)
        if match is None:
            return None
        obj = self.convert_groupdict(match.groupdict())
        output = AttrDict()
        for key, field in self.fields.items():
            value = field.load(obj)
            # If there is no value, don't include anything in the output dictionary
            if not is_valid(value):
                continue
            # If the value isn't a dict, or there's not flatten directive, add and continue
            if not isinstance(value, dict) or not getattr(field, "flatten", False):
                output[field.output_name] = value
                continue
            # Merge in flattened fields
            output.update(value)
        return output
    
    def convert_groupdict(self, obj):
        return obj

class ZipSchema(Schema):
    """
    This schema type allows fields that produce multiple values to be
    zipped together into records.
    """
    def bind(self, name=None, parent=None):
        super().bind(name, parent)
        new_fields = dict()
        for name, field in self.fields.items():
            new_fields[name] = f.List(field.__class__, getattr(field.accessor, "data_key", None))
        self.fields = new_fields

    def deserialize(self, obj) -> "Dict":
        result = unzip_records(super().deserialize(obj))
        return result