from .schema import Deserializer, Schema, PolymorphicSchema, RegexSchema, ZipSchema
from lxml.etree import XPath

try:
    from lxml.cssselect import CSSSelector as CSS
except ImportError:
    pass