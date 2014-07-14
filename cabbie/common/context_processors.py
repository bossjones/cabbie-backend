# -*- coding: utf-8 -*-

from django.conf import settings

from cabbie.utils.rand import random_hash


def default(request):
    context = {
        'settings': settings,
        'version': random_hash() if settings.DEBUG else settings.VERSION,
        'url_name': request.resolver_match.url_name
                    if request.resolver_match else None,
    }
    return context
