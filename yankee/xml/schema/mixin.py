import lxml.etree as ET

from .accessor import xpath_accessor

class XmlMixin(object):
    class Meta:
        accessor_function = xpath_accessor
        infer_keys = False

    def to_string(self, elem):
        return elem if isinstance(elem, str) else elem.text or ""

    def convert_groupdict(self, dictionary):
        root = ET.Element("root")
        for k, v in dictionary.items():
            subel = ET.SubElement(root, k)
            subel.text = v
        return root

    @property
    def raw_text(self):
        return ET.tostring(self.raw, pretty_print=True).decode()
