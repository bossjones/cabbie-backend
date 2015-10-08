import django.dispatch

post_request_rejected = django.dispatch.Signal(providing_args=['request'])

post_ride_requested = django.dispatch.Signal(providing_args=['ride'])
post_ride_approve = django.dispatch.Signal(providing_args=['ride'])
post_ride_reject = django.dispatch.Signal(providing_args=['ride'])
post_ride_cancel = django.dispatch.Signal(providing_args=['ride'])
post_ride_arrive = django.dispatch.Signal(providing_args=['ride'])
post_ride_board = django.dispatch.Signal(providing_args=['ride'])
post_ride_complete = django.dispatch.Signal(providing_args=['ride'])
post_ride_first_rated = django.dispatch.Signal(providing_args=['ride'])
post_ride_rated = django.dispatch.Signal(providing_args=['ride'])
