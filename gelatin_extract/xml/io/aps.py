from dataclasses import dataclass

@dataclass
class KV():
    key: str
    value: str

    @classmethod
    def from_line(cls, line):
        return cls(line[:5].strip(), line[5:].rstrip())

def process_chunk(chunk, record_tag):
    """Take a chunk that represents a record
    and returns an XML document"""
    doc = [f"<{record_tag}>",]
    last_line, chunk = chunk[0], chunk[1:]
    section = None
    for kv in chunk:
        if not kv.key: # line continuation
            if last_line.key == "TBL": # Preserve newlines on tables
                last_line.value += "\n" + kv.value
            else:
                last_line.value += kv.value
            continue
        
        if not last_line.value: # New Section
            if section:
                doc.append(f"</{section}>")
            doc.append(f"<{last_line.key}>")
            section = last_line.key
        else:
            doc.append(f"{'\t' if section else ''}<{last_line.key}>{last_line.value}</{last_line.key}>")
        last_line = kv
    doc.append(f"<{last_line.key}>{last_line.value}</{last_line.key}>")
    if section:
        doc.append(f"</{section}>")
    doc.append(f"</{record_tag}>")
    return "\n".join(doc).replace("&", "&amp;")


def aps_to_xml(file: "io.RawBytesIO", record_tag: "str") -> "str":
    """APS Iterator
    Will yield back XML-formatted documents for each
    record that begins with record_tag
    """
    chunk = list()
    recording = False
    for line in file:
        if not recording and record_tag not in line:
            continue
        if record_tag in line:
            recording = True
        kv = KV.from_line(line)
        if kv.key == record_tag and chunk:
            yield process_chunk(chunk, record_tag)
            chunk = list()
        else:
            chunk.append(kv)
    yield process_chunk(chunk, record_tag)