import io

import lxml.etree as ET

from .aps import aps_iterator, aps_record_to_xml

sample_doc = """
PATN
WKU  D04520599
APN  1348817
TTL  Pair of medium-heeled open-back shoes
ISD  20011218
TBL  ==========A FORMATTED TABLE==========
     -------------------------------------
INVT
NAM  Jacobs; Marc
ASSG
NAM  Louis Vuitton Malletier, S.A.
CTY  Paris
PRIR
CNT  FRX
APD  20000307
APN  00 3859
CLAS
OCL  D 2926
XCL   D2925
EDF  7
ICL  0204
UREF
PNO  D39412
ISD  19080700
NAM  Ostrowsky
OCL  D 2919
UREF
PNO  D95540
ISD  19350500
NAM  Perugia
OCL  D 2926
UREF
PNO  D190164
ISD  19610400
NAM  Lacek
OCL  D 2932""".strip()


def test_aps_conversion_from_string():
    result = aps_record_to_xml(sample_doc)
    tree = ET.fromstring(result)
    assert tree.find("./APN").text == "1348817"
    assert tree.find("./CLAS/OCL").text == "D 2926"
    assert len(tree.findall("./UREF")) == 3


def test_aps_conversion_from_bytes():
    result = aps_record_to_xml(sample_doc.encode())
    tree = ET.fromstring(result)
    assert tree.find("./APN").text == "1348817"
    assert tree.find("./CLAS/OCL").text == "D 2926"
    assert len(tree.findall("./UREF")) == 3


sample_docs = """
PATN
WKU  D04520599
PATN
WKU  101231241
PATN
WKU  123125123""".strip()


def test_aps_iterator():
    counter = 0
    for record in aps_iterator(io.BytesIO(sample_docs.encode()), record_tag="PATN"):
        tree = ET.fromstring(record)
        assert tree.find("./WKU").text
        counter += 1
    assert counter == 3
