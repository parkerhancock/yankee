# XML / HTML Loading

## Basic Import

XML and HTML parsing is handled identically. The only difference is that the HTML module uses the more permissive `lxml.html` parser and is more appropriate for handling HTML documents 

For **XML**, use this import statement:

```python
from yankee.xml.schema import Schema, fields as f, CSSSelector
```

For **HTML**, use this import statement:

```python
from yankee.html.schema import Schema, fields as f, CSSSelector
```

## Data Keys

Because XML structures are complex, keys cannot be inferred from field names. Instead, they must be defined in one of two ways: a string (which is intepreted as an XPath 1.0 expression) or a `CSS` object. By default, data keys passed as strings are assumed to be XPath 1.0 expressions. As an alternative, you can pass a CSSSelector object as a data key to use CSS selector expressions.

Both are supported by [lxml]. The documentation for their input values is here:

- [XPath](https://lxml.de/xpathxslt.html#xpath)
- [CSSSelector](https://lxml.de/cssselect.html#the-cssselector-class)

## Namespace Handling

Namespaces are a pain. But Yankee tries to make this easy. On whatever your base Schema is -- either your top-level Schema, or a parent class of that schema, you can set the special `namespaces` attribute on the `Meta` class as shown below. These prefixes will then be respected in all xpath queries used in the schema and all subschemas:

```python
from yankee.xml.schema import Schema, fields as f

class NestedXmlSchema(Schema):
    name = f.Str("./ns:name")

class ExampleXMLSchema(Schema):
    class Meta:
        namespaces = {
            "ns": "<url here>",
            "ops": "http://ops.epo.org"
        }
    nested_xml_schema = NestedXmlSchema("./ops:nested-object")

```
This `namespaces` attribute will be handed down to any nested schemas, so it only needs to be set on the top-level object. The format for the `namespaces` attribute is the same as that for the namespaces dictionary described in the [lxml documentation for XPath](https://lxml.de/xpathxslt.html)

## Input Documents

The XML/HTML modules are supported by the excellent [lxml] library. For an XML or HTML schema, the object passed to a Schemas `.load` method can be either `bytes`, `string`, or an `lxml.etree._Element` / `lxml.etree._ElementTree` object. If an `_Element` or `_ElementTree` object is provided, it is used directly. If a `str` or `bytes` object is provided, the appropriate `lxml` parser is used to parse the document - either `lxml.etree.fromstring` or `lxml.html.fromstring`.

[lxml]: https://lxml.de

## Complete Example

Take this:
```xml
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
```

Do this:
```python
from yankee.xml.schema import Schema, fields as f, CSSSelector

class XmlExample(Schema):
    name = f.String("./name")
    birthday = f.Date(CSSSelector("birthdate"))
    deep_data = f.Int("./something/many/levels/deep")

XmlExample().load(xml_doc)
```

Get this:
```python
{
    "name": "Johnny Appleseed",
    "birthday": datetime.date(2000, 1, 1),
    "deep_data": 123
}
```
