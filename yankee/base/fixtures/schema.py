from yankee.base import Schema, fields as f


class ObjectSchema(Schema):
    foo = f.Str()
    bar = f.Str()