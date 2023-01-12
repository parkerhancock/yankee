import io

from .iterparse import xml_iterparse

example_doc = """
<?xml version=1.0>
<collection>
<item>Some Text</item>
<item/>
<item/>
</collection>
<collection>
<item/>
</collection>"""


def test_xml_iterparse():
    counter = 0
    for el in xml_iterparse(io.BytesIO(example_doc.encode()), tag="item"):
        print(el)
        counter += 1
    assert counter == 4
