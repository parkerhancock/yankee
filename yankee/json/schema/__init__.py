from .fields import *
from .schema import PolymorphicSchema, Schema, RegexSchema, ZipSchema

try:
    import jsonpath_ng
    def JsonPath(string):
        try:
            return jsonpath_ng.parse(string)
        except jsonpath_ng.exceptions.JsonPathParserError:
            return jsonpath_ng.ext.parse(string)
except ImportError:
    pass

