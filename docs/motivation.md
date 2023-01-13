# Motivation

I do a lot of data parsing from legal and IP related data sources. A lot of that is out of XML and JSON source files. Parsing that can get ugly fast. I needed a simple, declarative way to get that data.

I looked at [marshmallow], which while a great library, had two key problems (1) a lack of XML parsing support, and (2) a requirement to be able to round-trip data. I needed XML parsing, and I didn't have any need to round trip the data. So I made this. It originally lived in my [patent_client] library, but as it matured, I moved it to its own separate library for more general use

[marshmallow]: https://marshmallow.readthedocs.io/en/stable/
[patent_client]: https://patent-client.readthedocs.io/en/latest/
