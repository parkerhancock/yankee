import re

us_re_1 = re.compile(r"([A-Z]+)([A-Z][a-z])")
us_re_2 = re.compile(r"([a-z\d])([A-Z])")
us_re_3 = re.compile(r"([^\d])(\d+)")


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
    return obj or isinstance(obj, (int, float))


# Cleans whitespace from text data
whitespace_re = re.compile(r"\s+")
clean_whitespace = lambda s: whitespace_re.sub(" ", s).strip().strip(",").strip()
