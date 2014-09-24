import django.dispatch


post_ride_complete = django.dispatch.Signal(providing_args=['ride'])
