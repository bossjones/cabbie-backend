import functools

from django.core.cache import cache


def cached(timeout, key=None):
    def decorator(func):
        base_key = key or func.__name__
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = u'{base_key}_{args}_{kwargs}'.format(
                base_key=base_key, args=tuple(args),
                kwargs=tuple(sorted(kwargs.items())),
            )
            value = cache.get(cache_key)
            if not value:
                value = func(*args, **kwargs)
                cache.set(cache_key, value, timeout)
            return value
        return wrapper
    return decorator
