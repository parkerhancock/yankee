# Gelatin Extract

This is kind of like Marshmallow, but only does deserialization. What it lacks in reversibility, it makes up for in speed. Schemas are compiled in advance allowing
deserialization to occur very quickly.

## Motivation

I have another package called patent_client. I also do a lot with legal data, some of which is in XML, and some of which is in JSON. But there's a lot of it. And I mean *a lot*, so speed matters.

## Quick Start

There are two main modules: `gelatin_extract.json.schema` and `gelatin_extract.xml.schema`. Those modules support defining class-style deserializers. Both start by subclassing a `Schema` class, and then defining attributes from the `fields` submodule.

### JSON Deserializer Example

```python
    from gelatin_extract.json.schema import Schema
    from gelatin_extract.json.schema import fields

    class JsonExample(Schema):
        name = fields.String()
        birthday = fields.Date("birthdate")
        deep_data = fields.Int("something.0.many.levels.deep")

    obj = {
        "name": "Johnny Appleseed",
        "birthdate": "2000-01-01",
        "something": [
            {"many": {
                "levels": {
                    "deep": 123
                }
            }}
        ]
    }

    JsonExample().deserialize(obj)
    # Returns
    {
        "name": "Johnny Appleseed",
        "birthday": datetime.date(2000, 1, 1),
        "deep_data": 123
    }

```

For JSON, the attributes are filled by pulling values off of the JSON object. If no
path is provided, then the attribute name is used. Otherwise, a dotted string
can be used to pluck an item from the JSON object.

### XML Deserializer Example

```python
    import lxml.etree as ET
    from sugar.xml.schema import Schema
    from sugar.xml.schema import fields

    class XmlExample(Schema):
        name = fields.String("./name")
        birthday = fields.Date("./birthdate")
        deep_data = fields.Int("./something/many/levels/deep")

    obj = ET.fromstring(b"""
    <xmlObject>
        <name>Johnny Appleseed</name>
        <birthdate>2000-01-01</birthdate>
        <something>
            <many>
                <levels>
                    <deep>123</deep>
                </levels>
            </many>
        </something>
    </xmlObject>
    """.strip())

    XmlExample().deserialize(obj)
    # Returns
    {
        "name": "Johnny Appleseed",
        "birthday": datetime.date(2000, 1, 1),
        "deep_data": 123
    }
```

For XML, the attributes are filled using XPath expressions. If no path is provided,
then the entire object is passed to the field (no implicit paths). Any valid Xpath
expression can be used.

