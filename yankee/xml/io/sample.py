from .autodetect import autodetect_format
from .iterparse import xml_iterparse


def sample_xml(
    in_file_obj: "io.RawIOBase", out_file_obj: "io.RawIOBase", n_records: int = 100
):
    chunk = in_file_obj.read(5000)
    format = autodetect_format(chunk)

    in_file_obj.seek(0)
    out_file_obj.write(format.preamble)
    for i, r in enumerate(xml_iterparse(in_file_obj, tag=format.item_tag)):
        out_file_obj.write(r)
        if i >= n_records:
            break
    out_file_obj.write(format.postamble)
