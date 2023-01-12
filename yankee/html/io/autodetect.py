import logging
import re
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class XmlFormat(object):
    item_tag: bytes
    list_tag: bytes
    preamble: bytes
    postamble: bytes
    namespaces: "Dict[str, str]"
    multidoc: bool


xml_doc_re = re.compile(r"\<\?xml".encode("utf-8"))
preamble_re = re.compile(
    r"(?P<preamble>^\<\?xml .*?>\s+<(?P<list_tag>[^\s]+).*?\>)\s*\<(?P<item_tag>[^\s]+).*?\>".encode(
        "utf-8"
    )
)


def get_namespaces(preamble):
    namespace_re = re.compile(r'xmlns:(?P<ns>[^=]+)="(?P<url>[^"]+)')
    namespace_matches = [m.groupdict() for m in namespace_re.finditer(preamble)]
    return {m["ns"]: m["url"] for m in namespace_matches}


def autodetect_format(chunk):
    """This function automatically detects the formatting of an XML
    record-style document, so long as it is fed a chunk that
    contains the doc declaration, wrapper element, and the opening tag
    of the first record
    """

    match = preamble_re.search(chunk).groupdict()
    preamble = match["preamble"].decode()
    list_tag = match["list_tag"].decode()
    item_tag = match["item_tag"].decode()
    postamble = f"</{list_tag}>"

    namespaces = get_namespaces(preamble)

    xml_docs = xml_doc_re.findall(chunk)
    multidoc = len(xml_docs) > 1
    return XmlFormat(item_tag, list_tag, preamble, postamble, namespaces, multidoc)
