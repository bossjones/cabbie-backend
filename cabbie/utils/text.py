import collections
import re


def strip_tags(s):
    return re.sub(r'<[^>]*?>', '', s)

def convert_to_byte(data, encoding='utf-8'):
    if isinstance(data, basestring):
        return data.encode(encoding) if isinstance(data, unicode) else \
               data
    elif isinstance(data, collections.Mapping):
        return dict(map(convert_to_byte, data.iteritems()))
    elif isinstance(data, collections.Iterable):
        return type(data)(map(convert_to_byte, data))
    else:
        return data

