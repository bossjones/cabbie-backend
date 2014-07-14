# Dictionary
# ----------

def pick(d, *args):
    keys = args
    if len(keys) == 1 and isinstance(keys[0], (list, tuple)):
        keys = keys[0]
    keys = set(keys)
    return dict([(k, v) for k, v in d.iteritems() if k in keys])
