# Strategy Outline

This is a data conversion library. We need to go from data in some format, and convert it to another. Our source formats are either XML or JSON, and we want a roughly unified interface for doing the data conversions.

Output data will always be plain Python objects


## JSON conversion

For json conversion, I want the user to be able to use implied keys, like:

```python

class ExampleSchema(Schema):
    some_field = f.Str()

```

which would be read as "someField" in accordance with JSON naming conventions. But if the user does this:

```python

class ExampleSchema(Schema):
    some_field = f.Str("some_field")

```

then no inflection conversion should occur. 


## Attribute Access

The goal with an attribute accessor would be to perform as much upfront processing as possible, providing a simple function to be called on the deserialized object to get the result. 