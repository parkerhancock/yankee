import lxml.etree as ET

from yankee.base.accessor import do_nothing

def xpath_accessor(data_key, name, many, meta):
    if not data_key:
        return do_nothing

    namespaces = getattr(meta, "namespaces", None)
    if many:
        xpath = ET.XPath(data_key, namespaces=namespaces)
    else:
        xpath = ET.XPath(f"({data_key})[1]", namespaces=namespaces)
    
    def accessor_func(obj):
        result = xpath(obj)
        try:
            return result if many else result[0]
        except IndexError:
            return None
    return accessor_func