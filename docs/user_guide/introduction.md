# Introduction to Yankee

## Basics
Yankee is about extracting data. Let's start with a simple example of extracting data from ordinary Python objects. You only need a single import statement:
```python
from yankee.base.schema import Schema, fields as f
```
Let's use the following example document:
```python
doc = {
    "name": "Johnny Appleseed",
    "birthdate": "1990-01-01",
    "age": "35"
    "children": ["Alice", "Bob"]
    "address": {
        "street": "123 Anywhere St.",
        "city": "San Francisco",
        "state": "California"
    }

}
```
To create a new data extractor, you need a `Schema` subclass that defines its fields as class members. Each `Field` object states its desired output data type, and a "data key" which defines where the data should be pulled from. All the basic Python types have a corresponding field type: `String`, `Int`, `Float`, `Boolean`, `Date`, `DateTime`, etc. A complete list is available in the Fields API reference.

This can be done like this:

```python
class PersonSchema(Schema):
    name = f.String(data_key="name")
    birthdate = f.Date(data_key="birthdate")
    age = f.Int(data_key="age")

```
Data can then be extracted by instantiating the object, and calling its `.load` method:
```python
result = PersonSchema().load(doc)
# produces
{
    "name": "Johnny Appleseed",
    "birthdate": datetime.date(1990, 1, 1),
    "age": 35
}
```
Note that the fields handle type casting, including for more complex types like `datetime.datetime` and `datetime.date` objects. Refer to the fields references for how type casting is accomplished.


Our schema can be simplified in two ways. First, every `Field` takes as its first argument a data key, and thus you can omit the keyword. Second, for some data types (Python and JSON), the key can be inferred from the field name. So this works too:

```python
class PersonSchema(Schema):
    name = f.String()
    birthdate = f.Date()
    age = f.Int()

```

## Lists of Data

Sometimes there is more than one value that we want in our output data. We can use the special `List` field to collect groups of data. The `List` field takes a `Field` as its first argument, and a `data_key` as its second argument. So we can get Johnny's children like this:

```python
class PersonSchema(Schema):
    #...
    children = f.List(f.Str, "children")
```

## Deeply Nested Data

Sometimes we want to get data deep inside an object. This can be accomplished by passing a data key that uses dot notation to get items deeper inside the object. All versions of `Schema` can do this, but refer to the specific one (for XML, JSON, HTML) for the rules on how those data keys are formed. For simple Python objects, this works:

```python
class PersonSchema(Schema):
    #...
    State = f.Str("address.state")
```

## Nested Schemas

Sometimes we want to capture nested data while preserving its structure. As it turns out, `Schema` objects can be used just like `Field` objects. So this works:

```python
class AddressSchema(Schema):
    street = f.Str()
    city = f.Str()
    state = f.Str()

class PersonSchema(Schema):
    #...
    address = AddressSchema()
```

## Circular Imports and Lazy Loading

Sometimes we have nested schemas that can create nasty circular references or import errors, like a self-referential Schema. The `Nested` field can be used to solve these problems. Just pass the name of the schema to `Nested`, and as long as the object referred to exists when the class is instantiated, it will find the right object. So this works:

```python
class PersonSchema(Schema):
    #...
    address = f.Nested("AddressSchema")

class AddressSchema(Schema):
    pass
```
