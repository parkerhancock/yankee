import ujson as json
import datetime
from dataclasses import dataclass, asdict

from .util import JsonEncoder
from yankee.util import is_valid

def convert_date(obj):
    if isinstance(obj, datetime.date):
        return datetime.datetime.combine(obj, datetime.datetime.min.time())
    return obj

@dataclass
class Row():
    def to_dict(self):
        return asdict(self, dict_factory=lambda i: dict([(k, v) for k, v in i if is_valid(v)]))

    def to_mongo(self):
        return asdict(self, dict_factory=lambda i: dict([(k, convert_date(v)) for k, v in i if is_valid(v)]))

    def to_pandas(self):
        """Convert object to Pandas Series"""
        import pandas as pd

        return pd.Series(self.to_dict())

    def to_json(self, *args, **kwargs):
        return json.dumps(self.to_dict(), *args, cls=JsonEncoder, **kwargs)