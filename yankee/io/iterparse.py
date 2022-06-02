import io
import re


def file_iterparse(
    in_file: io.RawIOBase, start: bytes, end: bytes = None
) -> "Iterable[bytes]":
    """
    Given an input file, and a start regex, yields individual records from the file
    Takes an optional end regex to eliminate unwanted or unnessary interstitial matter
    """
    buffer = bytearray()
    for event, chunk in file_event_parser(in_file, start, end):
        if event in ("start", "middle", "end"):
            buffer += chunk
        if event == "end":
            yield bytes(buffer)
            buffer = bytearray()


class NullObject(object):
    """A nothing object that returns null to all possible
    method calls"""

    def __getattr__(self, name: str) -> "Any":
        return self.null_function

    def null_function(self, *args, **kwargs):
        return None


def safe_search(string, regex):
    return regex.search(string) or NullObject()


def file_event_parser(
    in_file: io.RawIOBase, start: bytes, end: bytes = None, chunk_size=4000
) -> "Iterable[Tuple[str, bytes]]":
    """
    Given an input file, and a start and an optional end regex, yields
    "events" with chunks of the file.

    Inspired by etree.iterparse, yields back "events":
        None - preamble that isn't part of a record
        start - the start of a new record
        middle - continuation of a record
        end - the end of a record
    """
    if isinstance(start, (bytes, str)):
        if isinstance(start, str):
            start = start.encode()
        start = re.compile(start)
    if isinstance(end, (bytes, str)):
        if isinstance(end, str):
            end = end.encode()
        end = re.compile(end)

    chunk = bytearray()
    min_window_size = max((len(start.pattern), len(end.pattern) if end else 0))
    last_event = None
    while True:
        chunk_length = len(chunk)
        start_index = safe_search(chunk, start).start(0)
        end_index = safe_search(chunk, end).end(0) if end else None
        # Middle of Record
        if start_index is None and end_index is None:
            if last_event:
                yield ("middle", chunk)
                last_event = "middle"
            else:
                yield (None, chunk)
                last_event = None
            chunk = bytearray()

        # Start of Record
        elif (
            start_index is not None
            and end_index is None
            or (start_index and end_index and start_index < end_index)
        ):
            if last_event:
                yield ("end", chunk[:start_index])
                last_event = "end"
            else:
                yield (None, chunk[:start_index])
            yield ("start", chunk[start_index : start_index + len(start.pattern)])
            last_event = "start"
            chunk = chunk[start_index + len(start.pattern) :]
            recording = True

        # End of record
        elif (
            end_index is not None
            and start_index is None
            or (start_index and end_index and end_index < start_index)
        ):
            # It is implied that you are recording
            yield ("end", chunk[:end_index])
            last_event = "end"
            chunk = chunk[end_index:]
            last_event = None

        if chunk_length <= min_window_size:
            new_chunk = in_file.read(chunk_size)
            if not new_chunk:
                break
            chunk += new_chunk

    if last_event in ("middle", "start"):
        yield ("end", b"")
