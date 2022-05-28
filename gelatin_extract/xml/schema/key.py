from lxml.etree import XPath

def do_nothing(obj):
    return obj

class XmlMixin(object):
    def generate_key(self):
        if self.raw_key and self.many == False:
            return f"({self.raw_key})[1]"
        else:
            return self.raw_key

    def create_key_func(self):
        if self.key is None:
            return do_nothing           
        return XPath(self.key)

    def to_string(self, elem):
        return "".join(elem.itertext())
