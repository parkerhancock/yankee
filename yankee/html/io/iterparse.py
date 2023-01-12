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
    while True:
        nxt_chunk = in_f.read(chunk_size)
        if not nxt_chunk:
            yield chunk
            chunk = nxt_chunk
            continue
        end_tag = nxt_chunk.find(b">")
        yield chunk + nxt_chunk[:end_tag]
        chunk = nxt_chunk[end_tag:]
        
def iter_file(in_f, start_regex, end_regex, chunksize):
    pending = False
    chunk = bytearray()
    chunk_iter = safe_read(in_f, chunksize)
    chunk += next(chunk_iter)

    while True:
        if len(chunk) < chunksize:
            new_chunk = next(chunk_iter)
            chunk += new_chunk
        start = safe_search(chunk, start_regex).start(0)
        end = safe_search(chunk, end_regex).end(0)
        # Initialization - skip to first record
        if not pending and not start:
            chunk = bytearray()
        # Complete record within chunk
        elif start and end:
            yield ("start", chunk[start:end])
            yield ("end", bytearray())
            chunk = chunk[end:]
        # start detected, no open preceding item
        elif start and not pending:
            yield ("start", chunk[start:])
            chunk = bytearray()
        # end detected, open preceding item
        elif end and pending:
            yield ("end", chunk[:end])
            pending = False
            chunk = chunk[end:]
        # no start or end detected, but pending record
        elif not start and not end and pending:
            yield ("middle", chunk)
            chunk = bytearray()
        else:
            raise ValueError("Uncaught parser condition!")
        if not chunk and not new_chunk:
            break
            
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
    end_re = re.compile(f"</{tag}>|{tag}/>".encode())
    yield from iter_record(file_obj, start_re, end_re, chunksize)