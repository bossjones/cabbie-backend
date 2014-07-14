from cabbie.utils.format import (
    format_number, format_duration, format_price, format_percent, format_json)
from cabbie.utils.url import (
    add_url_param as do_add_url_param, absolutify as do_absolutify)
from cabbie.utils.text import strip_tags as do_strip_tags


# Format
# ------

def number(value, *args, **kwargs):
    return format_number(value, *args, **kwargs)

def duration(value, *args, **kwargs):
    return format_duration(value, *args, **kwargs)

def price(value, *args, **kwargs):
    return format_price(value, *args, **kwargs)

def percent(value, *args, **kwargs):
    return format_percent(value, *args, **kwargs)

def json(value, *args, **kwargs):
    return format_json(value, *args, **kwargs)


# String
# ------

def startswith(value, arg):
    return value.startswith(arg)

def endswith(value, arg):
    return value.endswith(arg)

def strip_tags(value):
    return do_strip_tags(value)

def boolean(value, true_display='true', false_display='false'):
    return true_display if value else false_display


# URL
# ---

def add_url_param(*args, **kwargs):
    return do_add_url_param(*args, **kwargs)

def absolutify(*args, **kwargs):
    return do_absolutify(*args, **kwargs)
