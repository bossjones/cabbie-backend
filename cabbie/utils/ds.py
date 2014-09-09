import re


# Dictionary
# ----------


def pick(d, *args):
    keys = args
    if len(keys) == 1 and isinstance(keys[0], (list, tuple)):
        keys = keys[0]
    keys = set(keys)
    return dict([(k, v) for k, v in d.iteritems() if k in keys])


def compact(things):
    if isinstance(things, basestring):
        return _compact(things)
    elif isinstance(things, (tuple, list)):
        return [_compact(thing) for thing in things if _compact(thing)]
    else:
        raise Exception('Unsupported type')


def _compact(thing):
    if isinstance(thing, basestring):
        return re.sub(r'\s+', ' ', thing.strip())
    return thing
