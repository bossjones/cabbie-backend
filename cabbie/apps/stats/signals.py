import django.dispatch

post_ride_rated = django.dispatch.Signal(providing_args=['ride'])
