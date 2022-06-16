import lxml.etree as ET

def do_nothing(obj):
    return obj

class FastXPath():
    def __init__(self, xpath, *args, many=False, **kwargs):
        self.many = many
        self.args = args
        self.kwargs = kwargs
        if not many:
            xpath = f"({xpath})[1]"
        self.xpath = xpath
        self.create_xpath_obj()
    
    def create_xpath_obj(self):
        self.xpath_obj = ET.XPath(self.xpath, *self.args, **self.kwargs)

    def __call__(self, *args, **kwargs):
        result = self.xpath_obj(*args, **kwargs)
        if self.many:
            return result
        elif result:
            return result[0]
        else:
            return None

    def __getstate__(self):
        state = self.__dict__.copy()
        del state['xpath_obj']
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self.create_xpath_obj()

class XmlMixin(object):
    def make_accessor(self):
        namespaces = getattr(self.Meta, "namespaces", dict())
        if self.data_key is None:
            return do_nothing
        return FastXPath(self.data_key, many=self.many, namespaces=namespaces)

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
