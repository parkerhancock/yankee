import lxml.etree as ET
from yankee.util import clean_whitespace

from .accessor import xml_accessor

class XmlMixin(object):
    list_field = "yankee.xml.schema.fields.List"
    
    class Meta:
        accessor_function = xml_accessor
        infer_keys = False

    def to_string(self, elem):
        if isinstance(elem, str):
            return elem
        elif isinstance(elem, ET._Comment):
            return clean_whitespace(elem.text, preserve_newlines=True)
        elif isinstance(elem, ET._Element):
            return clean_whitespace("".join(elem.itertext()), preserve_newlines=True)


    def convert_groupdict(self, dictionary):
        root = ET.Element("root")
        for k, v in dictionary.items():
            subel = ET.SubElement(root, k)
            subel.text = v
        return root

    @property
    def raw_text(self):
        return ET.tostring(self.raw, pretty_print=True).decode()
