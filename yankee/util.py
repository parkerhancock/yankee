import re
import itertools
import datetime
import ujson as json

us_re_1 = re.compile(r"([A-Z]+)([A-Z][a-z])")
us_re_2 = re.compile(r"([a-z\d])([A-Z])")
us_re_3 = re.compile(r"([^\d_])(\d+)")


def underscore(word: str) -> str:
    """
    Modified version from inflection library
    that also underscores digits
    """
    word = us_re_1.sub(r"\1_\2", word)
    word = us_re_2.sub(r"\1_\2", word)
    word = us_re_3.sub(r"\1_\2", word)
    word = word.replace("-", "_")
    return word.lower()


camelize_re = re.compile(r"(?:^|_)(.)")


def camelize(string: str) -> str:
    """
    Optimized version of the camelize function in inflections
    """
    result = camelize_re.sub(lambda m: m.group(1).upper(), string)
    return result[0].lower() + result[1:]


def is_valid(obj):
    if obj is None:
        return False
    elif isinstance(obj, (int, float)):
        return True
    elif isinstance(obj, (dict, list, str)) and len(obj) == 0:
        return False
    return True

def inflect(string, style=None):
    try:
        if style is None:
            return string
        elif style == "json":
            return camelize(string)
        elif style == "python":
            return underscore(string)
    except Exception:
        return None

# Cleans whitespace from text data
whitespace_re = re.compile(r"\s+")
clean_whitespace = lambda s: whitespace_re.sub(" ", s).strip().strip(",").strip()

strip_lines = lambda s: "\n".join(l.strip() for l in s.split("\n"))

def do_nothing(obj):
    return obj

def date_encoder(obj):
    if isinstance(obj, (datetime.date, datetime.datetime)):
        return obj.isoformat()
    raise ValueError(f"Object of type {type(obj)} is not serializable!")

class AttrDict(dict):    
    def __getattr__(self,  name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)
    
    def __setattr__(self, name, value):
        self[name] = value
    
    @classmethod
    def convert(cls, obj):
        if isinstance(obj, dict):
            return cls((k, cls.convert(v)) for k, v in obj.items())
        elif isinstance(obj, list):
            return list(cls.convert(i) for i in obj)
        else:
            return obj

    def to_json(self, *args, **kwargs):
        return json.dumps(self, *args, default=date_encoder, **kwargs)

def update_class(orig, update):
    for k in filter(lambda k: not k.startswith("_"), update.__dict__.keys()):
        setattr(orig, k, getattr(update, k))

def unzip_records(data):
    keys = list(data.keys())
    value_lists = [data[k] for k in keys]
    return list(AttrDict(zip(keys, o)) for o in itertools.zip_longest(*value_lists, fillvalue=None))