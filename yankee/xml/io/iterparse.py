import re

class NullObject(object):
    """A nothing object that returns null to all possible
    method calls"""

    def __getattr__(self, name: str) -> "Any":
        return self.null_function

    def null_function(self, *args, **kwargs):
        return None


def safe_search(string, regex):
    return regex.search(string) or NullObject()

def safe_read(in_f, chunk_size):
    chunk = in_f.read(chunk_size)
    nxt_chunk = b""
    while chunk:
        while chunk[-1] != ord(">"):
            nxt_chunk = in_f.read(100)
            idx = nxt_chunk.find(b">")
            if idx > 0:
                chunk += nxt_chunk[:idx+1]
                nxt_chunk = nxt_chunk[idx+1:]
            else:
                chunk += nxt_chunk
                nxt_chunk = b""
        yield chunk
        chunk = nxt_chunk + in_f.read(chunk_size)
        nxt_chunk = b""
        
def iter_file(in_f, start, end, chunksize):
    state = "no_record"
    chunk = bytearray()
    for new_chunk in safe_read(in_f, chunksize):
        chunk += new_chunk
        start = safe_search(chunk, start).start(0)
        end = safe_search(chunk, end).end(0)
        # Handle starts
        if state == "no_record" or state == "end":
            if start: 
                yield ("no_record", chunk[:start])
                state = "start"
                yield (state, chunk[start:])
                chunk = bytearray()
            else:
                state = "no_record"
                yield (state, chunk)
                chunk = bytearray()
        elif state == "start" or state == "middle":
            if end:
                state = "end"
                yield (state, chunk[:end])
                chunk = chunk[end:]
            else:
                state = "middle"
                yield (state, chunk)
                chunk = bytearray()
            
def iter_record(in_f, start, end, chunksize):
    record = bytearray()
    for event, chunk in iter_file(in_f, start, end, chunksize):
        if event == "start":
            record = chunk
        elif event == "middle":
            record += chunk
        elif event == "end":
            record += chunk
            yield bytes(record).strip()
            record = bytearray()

chunk_size = 30000

def xml_iterparse(file_obj: "io.RawBytesIO", tag=None, chunksize=chunk_size):
    start_re = re.compile(f"<{tag}".encode())
    end_re = re.compile(f"</{tag}>".encode())
    yield from iter_record(file_obj, start_re, end_re, chunksize)