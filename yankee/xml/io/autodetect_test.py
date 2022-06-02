from .autodetect import autodetect_format

example_doc = """<?xml version="1.0" encoding="UTF-8" ?>
<uspat:PatentBulkData xsi:schemaLocation="urn:us:gov:doc:uspto:patent ../../main/resources/Schema/USPatent/Document/PatentBulkData_V8_0.xsd" xmlns:pat="http://www.wipo.int/standards/XMLSchema/ST96/Patent" xmlns:uscom="urn:us:gov:doc:uspto:common" xmlns:uspat="urn:us:gov:doc:uspto:patent" xmlns:com="http://www.wipo.int/standards/XMLSchema/ST96/Common" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" com:st96Version="V3_1" com:ipoVersion="US_V8_0">
<uspat:PatentData com:st96Version="V4_0" com:ipoVersion="US_V9_0" xsi:schemaLocation="null null" xmlns:uspat="urn:us:gov:doc:uspto:patent" xmlns:tbl="http://www.oasis-open.org/tables/exchange/1.0" xmlns:pat="http://www.wipo.int/standards/XMLSchema/ST96/Patent" xmlns:uscom="urn:us:gov:doc:uspto:common" xmlns:m="http://www.w3.org/1998/Math/MathML3" xmlns:com="http://www.wipo.int/standards/XMLSchema/ST96/Common" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
    <uspat:PatentCaseMetadata>
        <uscom:ApplicationNumberText uscom:electronicText="02022946">02022946</uscom:ApplicationNumberText>
        <uscom:ApplicationTypeCategory>Utility</uscom:ApplicationTypeCategory>
        <uspat:PartyBag/>
        <uspat:ApplicationConfirmationNumber>1141</uspat:ApplicationConfirmationNumber>
        <uscom:BusinessEntityStatusCategory>UNDISCOUNTED</uscom:BusinessEntityStatusCategory>
        <pat:InventionTitle>N/A</pat:InventionTitle>
        <uscom:OfficialFileLocationDate>2000-01-21</uscom:OfficialFileLocationDate>
    </uspat:PatentCaseMetadata>
</uspat:PatentData>
<uspat:PatentData com:st96Version="V4_0" com:ipoVersion="US_V9_0" xsi:schemaLocation="null null" xmlns:uspat="urn:us:gov:doc:uspto:patent" xmlns:tbl="http://www.oasis-open.org/tables/exchange/1.0" xmlns:pat="http://www.wipo.int/standards/XMLSchema/ST96/Patent" xmlns:uscom="urn:us:gov:doc:uspto:common" xmlns:m="http://www.w3.org/1998/Math/MathML3" xmlns:com="http://www.wipo.int/standards/XMLSchema/ST96/Common" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
    <uspat:PatentCaseMetadata>
        <uscom:ApplicationNumberText uscom:electronicText="02000161">02000161</uscom:ApplicationNumberText>
        <uscom:ApplicationTypeCategory>Utility</uscom:ApplicationTypeCategory>
        <uspat:PartyBag/>
        <uspat:ApplicationConfirmationNumber>1014</uspat:ApplicationConfirmationNumber>
        <uscom:BusinessEntityStatusCategory>UNDISCOUNTED</uscom:BusinessEntityStatusCategory>
        <pat:InventionTitle>N/A</pat:InventionTitle>
        <uscom:OfficialFileLocationDate>2000-01-21</uscom:OfficialFileLocationDate>
    </uspat:PatentCaseMetadata>
</uspat:PatentData>
</uspat:PatentBulkData"""


def test_autodetect():
    format = autodetect_format(example_doc.encode())
    assert format.item_tag == "uspat:PatentData"
    assert format.list_tag == "uspat:PatentBulkData"
    assert (
        format.preamble
        == '<?xml version="1.0" encoding="UTF-8" ?>\n<uspat:PatentBulkData xsi:schemaLocation="urn:us:gov:doc:uspto:patent ../../main/resources/Schema/USPatent/Document/PatentBulkData_V8_0.xsd" xmlns:pat="http://www.wipo.int/standards/XMLSchema/ST96/Patent" xmlns:uscom="urn:us:gov:doc:uspto:common" xmlns:uspat="urn:us:gov:doc:uspto:patent" xmlns:com="http://www.wipo.int/standards/XMLSchema/ST96/Common" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" com:st96Version="V3_1" com:ipoVersion="US_V8_0">'
    )
    assert format.postamble == "</uspat:PatentBulkData>"
    assert format.multidoc == False
    assert format.namespaces == {
        "pat": "http://www.wipo.int/standards/XMLSchema/ST96/Patent",
        "uscom": "urn:us:gov:doc:uspto:common",
        "uspat": "urn:us:gov:doc:uspto:patent",
        "com": "http://www.wipo.int/standards/XMLSchema/ST96/Common",
        "xsi": "http://www.w3.org/2001/XMLSchema-instance",
    }


example_multidoc = """<?xml version="1.0" encoding="UTF-8" ?>
<uspat:PatentBulkData xsi:schemaLocation="urn:us:gov:doc:uspto:patent ../../main/resources/Schema/USPatent/Document/PatentBulkData_V8_0.xsd" xmlns:pat="http://www.wipo.int/standards/XMLSchema/ST96/Patent" xmlns:uscom="urn:us:gov:doc:uspto:common" xmlns:uspat="urn:us:gov:doc:uspto:patent" xmlns:com="http://www.wipo.int/standards/XMLSchema/ST96/Common" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" com:st96Version="V3_1" com:ipoVersion="US_V8_0">
<uspat:PatentData com:st96Version="V4_0" com:ipoVersion="US_V9_0" xsi:schemaLocation="null null" xmlns:uspat="urn:us:gov:doc:uspto:patent" xmlns:tbl="http://www.oasis-open.org/tables/exchange/1.0" xmlns:pat="http://www.wipo.int/standards/XMLSchema/ST96/Patent" xmlns:uscom="urn:us:gov:doc:uspto:common" xmlns:m="http://www.w3.org/1998/Math/MathML3" xmlns:com="http://www.wipo.int/standards/XMLSchema/ST96/Common" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
    <uspat:PatentCaseMetadata>
        <uscom:ApplicationNumberText uscom:electronicText="02022946">02022946</uscom:ApplicationNumberText>
        <uscom:ApplicationTypeCategory>Utility</uscom:ApplicationTypeCategory>
        <uspat:PartyBag/>
        <uspat:ApplicationConfirmationNumber>1141</uspat:ApplicationConfirmationNumber>
        <uscom:BusinessEntityStatusCategory>UNDISCOUNTED</uscom:BusinessEntityStatusCategory>
        <pat:InventionTitle>N/A</pat:InventionTitle>
        <uscom:OfficialFileLocationDate>2000-01-21</uscom:OfficialFileLocationDate>
    </uspat:PatentCaseMetadata>
</uspat:PatentData>
</uspat:PatentBulkData
<?xml version="1.0" encoding="UTF-8" ?>
<uspat:PatentBulkData xsi:schemaLocation="urn:us:gov:doc:uspto:patent ../../main/resources/Schema/USPatent/Document/PatentBulkData_V8_0.xsd" xmlns:pat="http://www.wipo.int/standards/XMLSchema/ST96/Patent" xmlns:uscom="urn:us:gov:doc:uspto:common" xmlns:uspat="urn:us:gov:doc:uspto:patent" xmlns:com="http://www.wipo.int/standards/XMLSchema/ST96/Common" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" com:st96Version="V3_1" com:ipoVersion="US_V8_0">
<uspat:PatentData com:st96Version="V4_0" com:ipoVersion="US_V9_0" xsi:schemaLocation="null null" xmlns:uspat="urn:us:gov:doc:uspto:patent" xmlns:tbl="http://www.oasis-open.org/tables/exchange/1.0" xmlns:pat="http://www.wipo.int/standards/XMLSchema/ST96/Patent" xmlns:uscom="urn:us:gov:doc:uspto:common" xmlns:m="http://www.w3.org/1998/Math/MathML3" xmlns:com="http://www.wipo.int/standards/XMLSchema/ST96/Common" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
    <uspat:PatentCaseMetadata>
        <uscom:ApplicationNumberText uscom:electronicText="02022946">02022946</uscom:ApplicationNumberText>
        <uscom:ApplicationTypeCategory>Utility</uscom:ApplicationTypeCategory>
        <uspat:PartyBag/>
        <uspat:ApplicationConfirmationNumber>1141</uspat:ApplicationConfirmationNumber>
        <uscom:BusinessEntityStatusCategory>UNDISCOUNTED</uscom:BusinessEntityStatusCategory>
        <pat:InventionTitle>N/A</pat:InventionTitle>
        <uscom:OfficialFileLocationDate>2000-01-21</uscom:OfficialFileLocationDate>
    </uspat:PatentCaseMetadata>
</uspat:PatentData>
</uspat:PatentBulkData"""


def test_autodetect_on_multidoc():
    format = autodetect_format(example_multidoc.encode())
    assert format.multidoc == True
