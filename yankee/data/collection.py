import json
import asyncio
from typing import TypeVar, Generic, AsyncIterator, Iterator, List, Union
from copy import deepcopy
from itertools import chain

from .util import JsonEncoder
from .row import Row
from .util import resolve
from .util import to_dict, ato_dict
from .attrdict import AttrDict

T = TypeVar("T")

class Collection(Generic[T]):
    def __init__(self, iterable):
        self.iterable = iterable

    def _sync_iterator(self) -> Iterator[T]:
        loop = asyncio.get_event_loop()
        agen = self.iterable.__aiter__()
        try:
            while True:
                yield loop.run_until_complete(agen.__anext__())
        except StopAsyncIteration:
            pass
        
    def __iter__(self) -> Iterator[T]:
        if hasattr(self.iterable, "__iter__"):
            return self.iterable.__iter__()
        return self._sync_iterator()
    
    async def _async_iterator(self) -> AsyncIterator[T]:
        for item in self.iterable:
            yield item
    
    def __aiter__(self) -> AsyncIterator[T]:
        if hasattr(self.iterable, "__aiter__"):
            return self.iterable.__aiter__()
        return self._async_iterator()

    def __repr__(self):
        if hasattr(self, "iterable"):
            return f"Collection({repr(self.iterable)})"
        return super().__repr__()

    def __add__(self, other):
        return Collection(chain(self, other))

    def to_list(self) -> List[T]:
        """Return a list of item objects from the Collection"""
        return list(self)
    
    async def ato_list(self) -> List[T]:
        """Return a list of item objects from the Collection"""
        return [o async for o in self]

    def to_records(self, item_class=dict, collection_class=list) -> List[dict]:
        """Return a list of dictionaries containing item data in ordinary Python types
        Useful for ingesting into NoSQL databases
        """
        return to_dict(self, item_class, collection_class)
    
    async def ato_records(self, item_class=dict, collection_class=list) -> List[dict]:
        return await ato_dict(self, item_class, collection_class)

    def to_mongo(self) -> List[dict]:
        """Return a list of dictionaries containing MongoDB compatible datatypes
        """
        return to_dict(self, dict, list, convert_dates=True)

    def to_json(self, *args, **kwargs) -> str:
        """Convert objects to JSON format"""
        return json.dumps(list(self.to_records()), *args, cls=JsonEncoder, **kwargs)
    
    async def ato_json(self, *args, **kwargs) -> str:
        """Convert objects to JSON format"""
        return json.dumps(await self.ato_records(), *args, cls=JsonEncoder, **kwargs)

    def to_pandas(self, annotate=list()) -> "pandas.DataFrame":
        """Convert Collection into a Pandas DataFrame"""
        import pandas as pd

        list_of_series = list()
        for i in iter(self):
            try:
                series = i.to_pandas()
            except AttributeError:
                series = pd.Series(i)
            for a in annotate:
                series[a] = resolve(i, a)
            list_of_series.append(series)
        return pd.DataFrame(list_of_series)
    
    async def ato_pandas(self, annotate=list()) -> "pandas.DataFrame":
        """Convert Collection into a Pandas DataFrame"""
        import pandas as pd

        list_of_series = list()
        async for i in self:
            try:
                series = i.to_pandas()
            except AttributeError:
                series = pd.Series(i)
            for a in annotate:
                series[a] = resolve(i, a)
            list_of_series.append(series)
        return pd.DataFrame(list_of_series)

    def explode(self, attribute, unpack=False, connector=".", prefix=True) -> Union["UnpackedCollection", "ExplodedCollection"]:
        """Implement an "explode" function for nested listed objects."""
        if unpack:
            return UnpackedCollection(ExplodedCollection(self, attribute), attribute, connector, prefix)
        else:
            return ExplodedCollection(self, attribute)

    def unpack(self, attribute, connector=".", prefix=True) -> "UnpackedCollection":
        """Implement an "unpack" function for nested single objects"""
        return UnpackedCollection(self, attribute, connector, prefix)

    # Values
    def values(self, *fields, **kw_fields) -> "ValuesCollection":
        """Return a Collection that will return a Row object for each item with a subset of attributes
        positional arguments will result in Row objects where the fields match the field names on the item,
        keyword arguments can be used to rename attributes. When passed as key=field, the resulting dictionary will have key: item[field]
        """
        return ValuesCollection(self, *fields, **kw_fields)

    def values_list(self, *fields, flat=False, **kw_fields) -> "ValuesListCollection":
        """Return a Collection that will return tuples for each item with a subset of attributes.
        If only a single field is passed, the keyword argument "flat" can be passed to return a simple list"""
        return ValuesListCollection(self, *fields, flat=flat, **kw_fields)

class ListCollection(list, Collection[T]):
    def __getitem__(self, sl) -> Union[T, List[T]]:
        result = list(self)[sl]
        if isinstance(sl, slice):
            return ListCollection(result)
        else:
            return result

class ExplodedCollection(Collection[T]):
    def __init__(self, iterable, attribute):
        self.iterable = iterable
        self.attribute = attribute

    def __iter__(self) -> Iterator[T]:
        for row in self.iterable:
            explode_field = resolve(row, self.attribute)
            for item in explode_field:
                if not isinstance(row, dict):
                    new_row = row.to_dict()
                else:
                    new_row = deepcopy(row)
                new_row[self.attribute] = item
                yield new_row
    
    async def _async_iterator(self) -> AsyncIterator[T]:
        async for row in self.iterable:
            explode_field = resolve(row, self.attribute)
            for item in explode_field:
                if not isinstance(row, dict):
                    new_row = row.to_dict()
                else:
                    new_row = deepcopy(row)
                new_row[self.attribute] = item
                yield new_row
    
    def __aiter__(self) -> AsyncIterator[T]:
        return self._async_iterator()


class UnpackedCollection(Collection[T]):
    def __init__(self, iterable, attribute, connector=".", prefix=True):
        self.iterable = iterable
        self.attribute = attribute
        self.connector = connector
        self.prefix = prefix

    def item_key(self, k):
        if not self.prefix:
            return k
        else:
            return f"{self.attribute}{self.connector}{k}"

    def __iter__(self) -> Iterator[dict]:
        for row in self.iterable:
            unpack_field = {self.item_key(k): v for k, v in resolve(row, self.attribute).items()}
            new_row = {**row, **unpack_field}
            del new_row[self.attribute]
            yield new_row

    async def _async_iterator(self):
        async for row in self.iterable:
            unpack_field = {self.item_key(k): v for k, v in resolve(row, self.attribute).items()}
            new_row = {**row, **unpack_field}
            del new_row[self.attribute]
            yield new_row

    def __aiter__(self) -> Iterator[dict]:
        return self._async_iterator()


class ValuesCollection(Collection):
    def __init__(self, collection, *arg_fields, fields=dict(), **kw_fields):
        self.collection = collection
        self.fields = {**{k: k for k in arg_fields}, **kw_fields, **fields}

    def __iter__(self) -> Iterator[AttrDict]:
        for item in self.collection:
            yield AttrDict((k, resolve(item, v)) for k, v in self.fields.items())
    
    async def _async_iterator(self):
        async for item in self.collection:
            yield AttrDict((k, resolve(item, v)) for k, v in self.fields.items())
    
    def __aiter__(self) -> AsyncIterator[AttrDict]:
       return self._async_iterator()

    def __getitem__(self, sl) -> Union[AttrDict, List[AttrDict]]:
        mger = deepcopy(self)
        new_mgr = mger.collection.__getitem__(sl)
        return new_mgr


class ValuesListCollection(ValuesCollection):
    def __init__(self, collections, *fields, flat=False, **kw_fields):
        super(ValuesListCollection, self).__init__(collections, *fields, **kw_fields)
        self.flat = flat

    def __iter__(self) -> Iterator[tuple]:
        if self.flat and len(self.fields) > 1:
            raise ValueError("Flat only works with 1 field!")
        for row in super(ValuesListCollection, self).__iter__():
            data = tuple(row.values())
            yield data[0] if self.flat else data
    
    async def _async_iterator(self):
        if self.flat and len(self.fields) > 1:
            raise ValueError("Flat only works with 1 field!")
        async for row in super(ValuesListCollection, self)._async_iterator():
            data = tuple(row.values())
            yield data[0] if self.flat else data
            
    def __aiter__(self) -> AsyncIterator[tuple]:
        return self._async_iterator()
