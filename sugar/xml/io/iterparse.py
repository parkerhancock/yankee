from file_utils.iterparse import file_iterparse


def xml_iterparse(file_obj:"io.RawBytesIO", tag=None):
    if not tag:
        return
    tag = tag.decode()
    start = f"<{tag}".encode("utf-8")
    end = f"(</{tag}>|{tag}.*?/>)".encode("utf-8")
    yield from file_iterparse(file_obj, start=start, end=end)
    
