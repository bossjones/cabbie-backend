from django.db.models.signals import post_save, post_delete

from cabbie.common.models import ActiveMixin
from cabbie.common.signals import post_create, post_activate, post_inactivate
from cabbie.utils.model import has_child_model


def _on_increment(instance, reverse=False):
    if hasattr(instance, 'get_incrementer'):
        incrementer = instance.get_incrementer(reverse)
        incrementer and incrementer.run()

def on_post_save(sender, instance, created, **kwargs):
    if created:
        post_create.send(sender=sender, instance=instance)

def on_post_create(sender, instance, **kwargs):
    if isinstance(instance, ActiveMixin):
        # If this instance is newly created but set as inactive, then do not
        # increment
        if not instance.is_active:
            return

    _on_increment(instance)

def on_post_delete(sender, instance, **kwargs):
    if isinstance(instance, ActiveMixin):
        # If this instance is already inactivated, do not decrement
        if not instance.is_active:
            return

    if has_child_model(instance):
        # When being deleted, post_delete signal is generated for parent model
        # as well so that incrementer is run twice, which is different behavior
        # from post_save. To avoid decrement related count multiple items,
        # the parent shouldn't process any incrementer in case of deletion.

        # TODO: What if the model itself has childrens but the instance
        # doesn't?
        return

    _on_increment(instance, reverse=True)

def on_post_activate(sender, instance, **kwargs):
    _on_increment(instance)

def on_post_inactivate(sender, instance, **kwargs):
    _on_increment(instance, reverse=True)

post_save.connect(on_post_save, dispatch_uid='from_common')
post_create.connect(on_post_create, dispatch_uid='from_common')
post_delete.connect(on_post_delete, dispatch_uid='from_common')
post_activate.connect(on_post_activate, dispatch_uid='from_common')
post_inactivate.connect(on_post_inactivate, dispatch_uid='from_common')

