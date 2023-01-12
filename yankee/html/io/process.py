import logging

import lxml.etree as ET
from file_utils import file_iterparse


class XmlProcessor(object):
    parser = None
    record_tag = None
    dtd_resolver = ET.Resolver

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        # Expand namespace declarations if present
        if self.record_tag and ":" in self.record_tag:
            ns, tag = self.record_tag.split(":")
            self.record_tag = f"{{{self.schema.Meta['ns'][ns]}}}{tag}"

    def process(self, file_obj, meta=None):
        parse_element = self._parse_element
        if self.multidoc:
            for el in self._process_multidoc(file_obj):
                yield parse_element(el, meta)
        else:
            for el in self._process_normal(file_obj):
                yield parse_element(el, meta)

    def _parse_element(self, el, meta):
        r = self.parser.deserialize(el)
        if meta is not None:
            r["meta"] = meta
        return r

    def _process_multidoc(self, file_obj):
        start = r"<\?xml".encode("utf-8")
        end = r"\n(?=\<\?xml)".encode("utf-8")
        xml_parser = ET.XMLParser(load_dtd=True, recover=True)
        xml_parser.resolvers.add(self.dtd_resolver())
        for r in file_iterparse(file_obj, start, end):
            yield xml_parser.fromstring(r)

    def _process_normal(self, file_obj):
        et_gen = ET.iterparse(
            file_obj, load_dtd=True, recover=True, tag=self.record_tag, events=("end",)
        )
        et_gen.resolvers.add(self.dtd_resolver())
        for _, el in et_gen:
            yield el
            el.clear()


def parse_multidoc(file_obj, xml_parser=None):
    start = r"<\?xml".encode("utf-8")
    end = r"\n(?=\<\?xml)".encode("utf-8")
    xml_parser = xml_parser or ET.XMLParser()
    for r in file_iterparse(file_obj, start, end):
        yield xml_parser.fromstring(r)


def parse_xml_file(file_obj, record_tag):
    for _, el in ET.iterparse(file_obj, tag=record_tag):
        yield el
        el.clear()
