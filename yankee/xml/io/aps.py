import io

from ...io.iterparse import file_iterparse


def aps_record_to_xml(text):
    if isinstance(text, str):
        buf = io.StringIO(text)
    else:
        buf = io.TextIOWrapper(io.BytesIO(text))
    record_tag = buf.readline().strip()
    output = list()
    output.append(f"<{record_tag}>")
    section_tag = None
    item_tag = None
    for line in buf.readlines():
        key = line[:5].strip()
        value = line[5:].strip()
        if key and not value:  # New Section
            if item_tag:
                output.append(f"</{item_tag}>")
                item_tag = None
            if section_tag:
                output.append(f"</{section_tag}>")
            output.append(f"<{key}>")
            section_tag = key
        elif value and not key:
            if item_tag == "TBL":
                output.append(f"{value}\n")
            else:
                output.append(value)
        else:
            # New Item
            if item_tag:
                output.append(f"</{item_tag}>")
            output.append(f"<{key}>")
            item_tag = key
            if item_tag == "TBL":
                output.append(f"{value}\n")
            else:
                output.append(value)
    if item_tag:
        output.append(f"</{item_tag}>")
    if section_tag:
        output.append(f"</{section_tag}>")
    output.append(f"</{record_tag}>")
    return "".join(output).encode()


def aps_iterator(file_obj: io.RawIOBase, record_tag=None):
    for record in file_iterparse(file_obj, start=record_tag.encode()):
        yield aps_record_to_xml(record)
