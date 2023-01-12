import lxml.etree as ET
from yankee.base.accessor import do_nothing

def html_accessor(data_key, name, many, meta):
    if isinstance(data_key, ET.XPath):
        def accessor_func(obj):
            if obj is None:
                return None
            result = data_key(obj)
            return result if many else result[0]
        return accessor_func
    
    if not data_key:
        return do_nothing

    namespaces = getattr(meta, "namespaces", None)
    if many:
        xpath = ET.XPath(data_key, namespaces=namespaces)
    else:
        xpath = ET.XPath(f"({data_key})[1]", namespaces=namespaces)
    
    def accessor_func(obj):
        if obj is None:
            return None
        result = xpath(obj)
        try:
            return result if many else result[0]
        except IndexError:
            return None
    return accessor_func