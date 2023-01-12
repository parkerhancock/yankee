import json
from dataclasses import dataclass, asdict

from .util import JsonEncoder
from yankee.util import is_valid

@dataclass
class Row():
    def to_dict(self):
        return asdict(self, dict_factory=lambda i: dict([(k, v) for k, v in i if is_valid(v)]))

    def to_pandas(self):
        """Convert object to Pandas Series"""
        import pandas as pd

        return pd.Series(self.to_dict())

    def to_json(self, *args, **kwargs):
        return json.dumps(self.to_dict(), *args, cls=JsonEncoder, **kwargs)