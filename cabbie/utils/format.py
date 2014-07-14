from xml.dom import minidom
import simplejson as json

from cabbie.utils.time_ import SECOND, MINUTE, HOUR, DAY, WEEK


def format_duration(s, verbose=False):
    s = int(s)
    days = int(s / DAY)
    s -= days * DAY
    hours = int(s / 3600)
    s -= hours * HOUR
    minutes = int(s / 60)
    s -= minutes * MINUTE
    seconds = s

    tokens = []
    if days > 0: tokens.append('{0}d'.format(days))
    if hours > 0: tokens.append('{0}h'.format(hours))
    if minutes > 0: tokens.append('{0}m'.format(minutes))
    if seconds > 0 or s == 0: tokens.append('{0}s'.format(seconds))

    if not verbose:
        tokens = tokens[:1]

    return ' '.join(tokens)

def format_number(number):
    block_size = 3

    tokens = str(number).split('.')
    suffix = '.%s' % tokens[1] if len(tokens) > 1 else ''
    old_str = tokens[0]
    new_str = ''
    length = len(old_str)

    for i in range(length):
        index = length - 1 - i
        if i / block_size > 0 and i % 3 == 0:
            new_str += ','
        new_str += old_str[index]

    return new_str[::-1] + suffix

def format_percent(ratio):
    return '{0}%'.format(int(float(ratio) * 100))

def format_price(price, currency='$', round=False):
    return '%s%.{0}f'.format(0 if round else 2) \
           % (currency, float(price))

def format_json(d, indent=4, sort_keys=True):
    return json.dumps(d, indent=indent, sort_keys=sort_keys)

def format_xml(xml_string):
    xml = minidom.parseString(xml_string)
    return xml.toprettyxml()
