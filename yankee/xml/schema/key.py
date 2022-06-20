import lxml.etree as ET
from yankee.base.deserializer import DefaultAccessor

def do_nothing(obj):
    return obj

class XPathAccessor(DefaultAccessor):
    def __init__(self, *args, namespaces=dict(), **kwargs):
        self.namespaces = namespaces
        super().__init__(*args, **kwargs)

    def make_path_obj(self):
        if self.data_key is None:
            return do_nothing
        if not self.many and not self.filter:
            xpath = f"({self.data_key})[1]"
        else:
            xpath = self.data_key
        return ET.XPath(xpath, namespaces=self.namespaces)


class XmlMixin(object):
    def make_accessor(self, data_key, name, many, filter):
        namespaces = getattr(self.Meta, "namespaces", dict())
        if data_key is None and filter is None:
            return do_nothing
        return XPathAccessor(data_key, many=many, filter=filter, namespaces=namespaces)

    def to_string(self, elem):
        if isinstance(elem, str):
            return elem
        try:
            return "".join(elem.itertext())
        except ValueError:
            # Occasionally elements won't have itertext available
            return elem.text

    def convert_groupdict(self, dictionary):
        root = ET.Element("root")
        for k, v in dictionary.items():
            subel = ET.SubElement(root, k)
            subel.text = v
        return root
