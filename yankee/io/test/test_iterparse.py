import io

from ..iterparse import file_iterparse

test_doc = """
<record>
<record>
<record>
<record>
"""


def test_file_iterparse_with_record_start():
    records = list(file_iterparse(io.BytesIO(test_doc.encode()), "<"))
    assert len(records) == 4
