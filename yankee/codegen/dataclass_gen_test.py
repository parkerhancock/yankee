import dataclasses as dc
from .dataclass_gen import generate_dc_code
from yankee.data import Row
from pathlib import Path

import pytest

@dc.dataclass
class Example(Row):
    a: int = None
    b: "List" = dc.field(default_factory=list)

    def example_function(self):
        pass
@pytest.mark.skip("WIP")
def test_generate_dc_code():
    source = generate_dc_code(Example)
    with (Path(__file__).parent / "example.py").open("w") as f:
        f.write(source)
    assert True