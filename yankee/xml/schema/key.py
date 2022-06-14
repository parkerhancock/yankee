from lxml.etree import XPath


def do_nothing(obj):
    return obj

class FastXPath(XPath):
    def __init__(self, xpath, *args, many=False, **kwargs):
        self.many = many
        if many:
            super().__init__(xpath, *args, **kwargs)
        else:
            xpath = f"({xpath})[1]"
            super().__init__(xpath, *args, **kwargs)
    
    def __call__(self, *args, **kwargs):
        result = super().__call__(*args, **kwargs)
        if self.many:
            return result
        elif result:
            return result[0]
        else:
            return None

class XmlMixin(object):
    def make_accessor(self):
        namespaces = getattr(self.Meta, "namespaces", dict())
        if self.data_key is None:
            return do_nothing
        return FastXPath(self.data_key, many=self.many, namespaces=namespaces)

    def to_string(self, elem):
        return "".join(elem.itertext())
