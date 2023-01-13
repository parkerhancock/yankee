# JSON Loading

## Basic Import

For **JSON**, use this import statement:

```python
from yankee.json.schema import Schema, fields as f
```

## Data Keys

Data keys can be defined in two ways. Either they are inferred from the fieldname, or they are defined expressly as `JSONPath` objects. 

**Inferred Data Keys:** This library assumes that the input JSON document follows the typical JSON convention of using camelCase fieldnames, as opposed to the Python convention of using snake_case class attributes. As a result, field names are inflected into camelCase as part of the key inference process. So a field named "first_name" will use "firstName" as its data key.

**Explicit Data Keys:** If a data key is provided as a string, it is interpreted as a JSON Path expression. These expressions are supported by the [jsonpath_ng] library, which provides documentation on JSON Path syntax.

[jsonpath_ng]: https://github.com/h2non/jsonpath-ng

## Input Documents

The JSON module is supported by the excellent [UltraJSON] library. For a JSON schema, the object passed to a Schemas `.load` method can be either `string`, or a `dict` object. If a `dict` object is provided, it is used directly. If a `str` object is provided, it is loaded using `ujson.loads`.

[UltraJSON]: https://github.com/ultrajson/ultrajson

## Complete Example

Take this:
```json
{
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
```
Do this:
```python
from yankee.json.schema import Schema, fields as f

class JsonExample(Schema):
    name = f.String()
    birthday = f.Date("birthdate")
    deep_data = f.Int("something.0.many.levels.deep")
```
Get this:
```python
{
    "name": "Johnny Appleseed",
    "birthday": datetime.date(2000, 1, 1),
    "deep_data": 123
}
```