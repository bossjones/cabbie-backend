import os
import random
import string

from cabbie.utils.hash import get_hash_value


def random_hash():
    return get_hash_value(os.urandom(100))


def random_string(length):
    random.seed(os.urandom(100))
    return ''.join(random.choice(string.ascii_lowercase + string.digits)
                   for x in range(length))
