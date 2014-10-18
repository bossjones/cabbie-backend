import django.dispatch


post_ride_board = django.dispatch.Signal(providing_args=['ride'])
