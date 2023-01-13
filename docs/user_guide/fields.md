# Fields

## Basic Field Types

There are basic fields to support Python datatypes. A few have unique options that affect how the type casting process works:

```{eval-rst}
.. autoclass:: yankee.base.fields.Field

.. autoclass:: yankee.base.fields.String

.. autoclass:: yankee.base.fields.Integer

.. autoclass:: yankee.base.fields.Float

.. autoclass:: yankee.base.fields.Boolean

.. autoclass:: yankee.base.fields.DateTime

.. autoclass:: yankee.base.fields.Date

```

## Special Field Types

There are also a few special types for common use cases

```{eval-rst}
.. autoclass:: yankee.base.fields.Const

.. autoclass:: yankee.base.fields.Exists
```

## Schema-Like fields

There are more fields that behave a bit like Schemas, in that they have subfields:

```{eval-rst}
.. autoclass:: yankee.base.fields.Combine

.. autoclass:: yankee.base.fields.DelimitedString

.. autoclass:: yankee.base.fields.Dictionary

.. autoclass:: yankee.base.fields.Alternative
```