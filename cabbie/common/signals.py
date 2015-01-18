import django.dispatch
from django.db.models.signals import post_delete

post_create = django.dispatch.Signal(providing_args=['instance'])
post_delete = post_delete
post_activate = django.dispatch.Signal(providing_args=['instance'])
post_inactivate = django.dispatch.Signal(providing_args=['instance'])
post_status_change = django.dispatch.Signal(
    providing_args=['instance', 'old_status', 'new_status', 'note'])
