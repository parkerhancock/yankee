import lxml.etree as ET

def do_nothing(obj):
    return obj

class FastXPath(ET.XPath):
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
        if isinstance(elem, str):
            return elem
        return "".join(elem.itertext())

    def convert_groupdict(self, dictionary):
        root = ET.Element("root")
        for k, v in dictionary.items():
            subel = ET.SubElement(root, k)
            subel.text = v
        return root
