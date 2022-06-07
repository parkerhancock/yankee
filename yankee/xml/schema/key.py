from lxml.etree import XPath


def do_nothing(obj):
    return obj


class XmlMixin(object):
    def make_accessor(self):
        namespaces = getattr(self.Meta, "namespaces", dict())
        if self.data_key is None:
            return do_nothing
        if self.data_key and self.many == False:
            return XPath(f"({self.data_key})[1]", namespaces=namespaces)
        else:
            return XPath(self.data_key, namespaces=namespaces)

    def to_string(self, elem):
        return "".join(elem.itertext())
