# XPath Utilites

# XPath Node Set Operations
def xpath_intersection(ns1, ns2):
    """The Kaysian Method for XPath 1.0 intersections
    Do not include leading . in ns1 and ns2"""
    return f"{ns1}[count(.|{ns2})=count({ns2})]"

def xpath_difference(ns1, ns2):
    """The Kaysian Method for XPath 1.0 differences
    Do not include leading . in ns1 and ns2"""
    return f"{ns1}[count({ns1}) != count({ns2})]"