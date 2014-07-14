import hashlib


def get_hash_value(value):
    return hashlib.sha1(value).hexdigest()
