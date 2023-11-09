import re
import dataclasses as dc
import importlib
import copy
from yankee.util import is_valid, AttrDict, clean_whitespace, unzip_records, import_class
from yankee import settings
from yankee.data import Row, AttrDict
from .deserializer import Deserializer, DefaultMeta
from .accessor import python_accessor
from yankee.data.collection import Collection, ListCollection

class Schema(Deserializer):
    output_type = dict
    __model__ = None
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

    def bind(self, name=None, parent=None, meta=None):
        super().bind(name, parent)
        # Make sure that fields are grabbed from superclasses as well
        self.fields = self.get_fields()
        self.bind_fields()

    def bind_fields(self, meta=None):
        for name, field in self.fields.items():
            if self.prefix:
                field.bind(f"{self.name}_{name}", self, meta)
            else:
                field.bind(name, self, meta)

    def get_fields(self):
        class_fields = list()
        for c in reversed(self.__class__.mro()):
            class_fields += [
                (k, v) for k, v in c.__dict__.items() if isinstance(v, Deserializer)
            ]
        return dict(class_fields)

    def get_model(self):
        # Model class is expressly there
        if not isinstance(self.__model__, str) and self.__model__ is not None:
            return
        # Model should be obtained from a string
        model_str = getattr(self, "__model_name__", False) or self.__class__.__name__.replace("Schema", "")
        *module, _model = model_str.rsplit(".", 1)
        module = self.__class__.__module__.replace(".schema", ".model")
        try:
            self.__model__ = getattr(importlib.import_module(module), _model)
        except (ImportError, AttributeError) as e:
            if isinstance(e, AttributeError) and "circular import" in str(e):
                raise e
            self.__model__ = self.make_dataclass()
        
    def load(self, obj):
        if settings.use_model:
            self.get_model()
        return super().load(obj)

    def deserialize(self, obj) -> "Dict":
        output = AttrDict()
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
        return output

    def load_model(self, obj):
        return self.__model__(**obj)

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
        return ListCollection(self.load(o) for o in objs)


class PolymorphicSchema(Schema):
    def bind(self, name=None, parent=None, meta=None):
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
            return dict()
        text = clean_whitespace(self.to_string(obj))
        match = self._regex.search(text)
        if match is None:
            return dict()
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

    def bind_fields(self, meta=None):
        return super().bind_fields(DefaultMeta)
    
    def convert_groupdict(self, obj):
        return obj

    def to_string(self, elem):
        return str(elem)

class ZipSchema(Schema):
    """
    This schema type allows fields that produce multiple values to be
    zipped together into records.
    """
    def __init__(self, *args, **kwargs):
        self.list_field = import_class(self.list_field)
        super().__init__(*args, **kwargs)

    def bind(self, name=None, parent=None, meta=None):
        super().bind(name, parent)
        new_fields = dict()
        for name, field in self.fields.items():
            f_copy = copy.deepcopy(field)
            list_field = self.list_field(f_copy, field.data_key)
            f_copy.data_key = False
            f_copy.make_accessor()
            list_field.output_name = field.output_name
            new_fields[name] = list_field
        self.fields = new_fields

    def deserialize(self, obj) -> "Dict":
        result = unzip_records(super().deserialize(obj))
        return result

    def load_model(self, obj):
        return [self.__model__(**o) for o in obj]
