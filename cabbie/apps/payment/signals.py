import django.dispatch


return_processed = django.dispatch.Signal(providing_args=['return_'])
coupon_processed = django.dispatch.Signal(providing_args=['coupon'])
