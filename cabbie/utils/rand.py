import os
import random
import string

from cabbie.utils.hash import get_hash_value


class Dice(object):
    """Simple dice class to randomly choose one value from a list based on
    weight. It's basically same as random.choice, but you can specify the odds
    for each element.
    """

    def __init__(self, *odds):
        if odds and (not odds[0] or isinstance(odds[0][0], (list, tuple))):
            odds = odds[0]
        self._odds = dict(odds)

    def __unicode__(self):
        return u'{0}({1})'.format(self.__class__.__name__, self._odds)

    def __repr__(self):
        return self.__unicode__()

    def __call__(self):
        return self.roll()

    def has(self, value):
        return value in self._odds

    def get_odd(self, value):
        return self._odds.get(value)

    def remove_odd(self, value):
        return self._odds.pop(value, None)

    def keys(self):
        return self._odds.keys()

    def add_odd(self, value, odd=1):
        assert odd >= 0, 'Should be bigger than zero'
        self._odds[value] = odd
        return self

    def add_odds(self, odds):
        for odd in odds:
            self.add_odd(*odd)
        return self

    def set_odd(self, value, odd):
        self.add_odd(value, odd)
        return self

    def roll(self):
        assert len(self._odds) > 0, 'No odd to roll'

        _random_seed()

        total = sum(odd for odd in self._odds.itervalues())
        pick = random.uniform(0, total)
        upto = 0.0

        for value, odd in self._odds.iteritems():
            if upto + odd > pick:
                return value
            upto += odd

        assert False, 'Shouldn\'t get here'


def random_hash():
    return get_hash_value(os.urandom(100))


def random_string(length):
    _random_seed()
    return ''.join(random.choice(string.ascii_lowercase + string.digits)
                   for x in range(length))


def random_int(start, end):
    _random_seed()
    return random.randint(start, end)


def random_float(start, end):
    _random_seed()
    return start + random.random() * (end - start)


def random_digit():
    return random_int(0, 9)


def random_gauss(mu, std=None):
    _random_seed()
    return random.gauss(mu, std or float(mu) / 4)


def weighted_choice(odds):
    return Dice(odds).roll()


def weighted_boolean(true_odd, false_odd):
    return weighted_choice((
        (True, true_odd),
        (False, true_odd),
    ))


def _random_seed():
    try:
        random.seed(os.urandom(100))
    except OSError:
        pass
