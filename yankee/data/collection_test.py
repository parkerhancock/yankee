import pytest
import json

from .collection import Collection

class TestCollection():
    def test_sync_iterable(self, event_loop):
        iterable = ["a", "b", "c"]
        collection = Collection(iterable)
        assert [o for o in collection] == iterable
        
    def test_async_iterable(self, event_loop):
        iterable = ["a", "b", "c"]
        async def gen():
            for i in iterable:
                yield i
        collection = Collection(gen())
        assert [o for o in collection] == iterable
        
    def test_list_conversion(self):
        iterable = ["a", "b", "c"]
        collection = Collection(iterable)
        assert collection.to_list() == iterable
        
    def test_records_conversion(self):
        iterable = [{"a": 1}, {"a": 2}]
        collection = Collection(iterable)
        assert collection.to_records() == iterable
        
    def test_json_conversion(self):
        iterable = [{"a": 1}, {"a": 2}]
        collection = Collection(iterable)
        assert json.loads(collection.to_json()) == iterable
        
    def test_pandas_conversion(self):
        iterable = [{"a": 1}, {"a": 2}]
        collection = Collection(iterable)
        assert collection.to_pandas().a.tolist() == [1, 2]
        
    

class TestCollectionAsync():
    @pytest.mark.asyncio
    async def test_sync_iterable(self, event_loop):
        iterable = ["a", "b", "c"]
        collection = Collection(iterable)
        assert [o async for o in collection] == iterable
        
    @pytest.mark.asyncio
    async def test_async_iterable(self, event_loop):
        iterable = ["a", "b", "c"]
        async def gen():
            for i in iterable:
                yield i
        collection = Collection(gen())
        assert [o async for o in collection] == iterable
        
    @pytest.mark.asyncio
    async def test_list_conversion(self):
        iterable = ["a", "b", "c"]
        collection = Collection(iterable)
        assert await collection.ato_list() == iterable
        
    @pytest.mark.asyncio
    async def test_records_conversion(self):
        iterable = [{"a": 1}, {"a": 2}]
        collection = Collection(iterable)
        assert await collection.ato_records() == iterable
        
    @pytest.mark.asyncio
    async def test_json_conversion(self):
        iterable = [{"a": 1}, {"a": 2}]
        collection = Collection(iterable)
        assert json.loads(await collection.ato_json()) == iterable
        
    @pytest.mark.asyncio
    async def test_pandas_conversion(self):
        iterable = [{"a": 1}, {"a": 2}]
        collection = Collection(iterable)
        df = await collection.ato_pandas()
        assert df.a.tolist() == [1, 2]
        
        
explode_data = [
    {"a": 1, "b": [2, 3]},
    {"a": 2, "b": [4, 5]},
]
        
class TestExplode():
    def test_can_do_basic_explode(self):
        collection = Collection(explode_data)
        exploded = collection.explode("b").to_list()
        assert len(exploded) == 4
        assert exploded == [
            {"a": 1, "b": 2},
            {"a": 1, "b": 3},
            {"a": 2, "b": 4},
            {"a": 2, "b": 5},
        ]

        
class TestExplodeAsync():
    @pytest.mark.asyncio
    async def test_can_do_basic_explode(self):
        collection = Collection(explode_data)
        exploded = await collection.explode("b").ato_list()
        assert len(exploded) == 4
        assert exploded == [
            {"a": 1, "b": 2},
            {"a": 1, "b": 3},
            {"a": 2, "b": 4},
            {"a": 2, "b": 5},
        ]

unpack_data = [
    {"a": 1, "b": {"c": 2, "d": 3}},
    {"a": 2, "b": {"c": 4, "d": 5}},
]

class TestUnpack():
    def test_can_do_basic_unpack(self):
        collection = Collection(unpack_data)
        unpacked = collection.unpack("b").to_list()
        assert len(unpacked) == 2
        assert unpacked == [
            {"a": 1, "b.c": 2, "b.d": 3},
            {"a": 2, "b.c": 4, "b.d": 5},
        ]
        
class TestUnpackAsync():
    @pytest.mark.asyncio
    async def test_can_do_basic_unpack(self):
        collection = Collection(unpack_data)
        unpacked = await collection.unpack("b").ato_list()
        assert len(unpacked) == 2
        assert unpacked == [
            {"a": 1, "b.c": 2, "b.d": 3},
            {"a": 2, "b.c": 4, "b.d": 5},
        ]

values_data = [
    {"a": 1, "b": 2, "c": 3},
    {"a": 2, "b": 4, "c": 5},
]

class TestValues():
    def test_can_do_basic_values(self):
        collection = Collection(values_data)
        values = collection.values("a", "c").to_list()
        assert len(values) == 2
        assert values == [
            {"a": 1, "c": 3},
            {"a": 2, "c": 5},
        ]
        
class TestValuesAsync():
    @pytest.mark.asyncio
    async def test_can_do_basic_values(self):
        collection = Collection(values_data)
        values = [o async for o in collection.values("a", "c")]
        assert len(values) == 2
        assert values == [
            {"a": 1, "c": 3},
            {"a": 2, "c": 5},
        ]
        
class TestValuesList():
    def test_can_do_basic_values(self):
        collection = Collection(values_data)
        values = collection.values_list("a", "c").to_list()
        assert len(values) == 2
        assert values == [
            (1, 3),
            (2, 5),
        ]
        
class TestValuesListAsync():
    @pytest.mark.asyncio
    async def test_can_do_basic_values(self):
        collection = Collection(values_data)
        values = [o async for o in collection.values_list("a", "c")]
        assert len(values) == 2
        assert values == [
            (1, 3),
            (2, 5),
        ]
    
    @pytest.mark.asyncio
    async def test_can_do_for_loops(self):
        collection = Collection(values_data)
        values = list()
        async for o in collection.values_list("a", "c"):
            values.append(o)
        assert len(values) == 2
        assert values == [
            (1, 3),
            (2, 5),
        ]