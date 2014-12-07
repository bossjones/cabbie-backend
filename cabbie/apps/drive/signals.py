import django.dispatch


post_ride_board = django.dispatch.Signal(providing_args=['ride'])
post_ride_complete = django.dispatch.Signal(providing_args=['ride'])
post_ride_rated = django.dispatch.Signal(providing_args=['ride'])
