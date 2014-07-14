import cStringIO
import os

from django.core.files import File
from django.core.files.storage import default_storage
from django.db import models
from django.db.models import Max
from django.db.models.fields.related import RelatedField
from django.template.defaultfilters import slugify
from django.utils import timezone
import requests

from cabbie.common.signals import (post_activate, post_inactivate,
                                   post_status_change)
from cabbie.utils.ds import pick
from cabbie.utils.increment import Incrementer
from cabbie.utils.rand import random_hash


Buffer = cStringIO.StringIO


# Base Mixins
# -----------

class UpdateMixin(object):
    def update(self, **kwargs):
        fields = self._meta.fields
        field_dict = dict(reduce(list.__add__, [
            [(field.name, field), (field.get_attname(), field)]
            for field in fields]))
        field_names = set(reduce(list.__add__, [
            [field.name, field.get_attname()] for field in fields], []))

        kwargs = pick(kwargs, *field_names)

        if kwargs:
            update_fields = []
            for key, value in kwargs.iteritems():
                convert = field_dict[key].to_python
                if convert(value) != convert(getattr(self, key)):
                    setattr(self, key, value)
                    update_fields.append(key)
            if update_fields:
                self.save(update_fields=update_fields)


class JSONMixin(object):
    def for_json(self, excludes=None):
        data = {}
        for field in self._meta.local_fields:
            if isinstance(field, RelatedField):
                data[field.attname] = getattr(self, field.attname)
            else:
                name = field.name
                if excludes and name in excludes:
                    continue
                value = getattr(self, name)
                if not isinstance(value, models.Model):
                    data[name] = value
        return data


class IncrementMixin(object):
    def get_incrementer(self, reverse=False):
        return Incrementer(reverse)


# Model Mixins
# ------------

class StatusMixin(models.Model):
    STATUS_FIELD_NAME = 'status'

    # The `status` field choices varies depending on the model defining it
    # so it should be manually added

    status_note = models.TextField(blank=True)
    status_changed_at = models.DateTimeField(default=timezone.now,
                                             editable=False)

    class Meta:
        abstract = True

    def change_status(self, status, note=None):
        if getattr(self, self.STATUS_FIELD_NAME) == status:
            return
        old_status = getattr(self, self.STATUS_FIELD_NAME)
        setattr(self, self.STATUS_FIELD_NAME, status)
        self.status_note = note or ''
        self.status_changed_at = timezone.now()
        self.save(update_fields=[self.STATUS_FIELD_NAME, 'status_note',
                                 'status_changed_at'])

        post_status_change.send(sender=self.__class__, instance=self,
                                old_status=old_status, new_status=status,
                                note=self.status_note)


class TimestampMixin(models.Model):
    created_at = models.DateTimeField(default=timezone.now, db_index=True,
                                      editable=False)
    updated_at = models.DateTimeField(default=timezone.now, db_index=True,
                                      editable=False)

    class Meta:
        abstract = True
        ordering = ['-created_at']

    def touch(self):
        self.save(update_fields=[])

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.updated_at = timezone.now()
        if update_fields is not None:
            update_fields.append('updated_at')
        super(TimestampMixin, self).save(
            force_insert, force_update, using, update_fields)


class SlugMixin(models.Model):
    SLUG_SOURCE_FIELD_NAME = 'name'
    SLUG_FIELD_NAME = 'slug'

    # The `name`  and `slug` fields vary depending on the model defining it
    # so it should be manually added

    class Meta:
        abstract = True

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        setattr(self, self.SLUG_FIELD_NAME,
                slugify(getattr(self, self.SLUG_SOURCE_FIELD_NAME)))

        if update_fields is not None:
            update_fields.append(self.SLUG_FIELD_NAME)

        super(SlugMixin, self).save(force_insert, force_update, using,
                                    update_fields)


class ActiveMixin(models.Model):
    is_active = models.BooleanField(
        'active', default=True, db_index=True,
        help_text='Designates whether this object should be treated as '
                  'active. Unselect this instead of deleting.')
    inactive_note = models.CharField(max_length=1000, blank=True)
    active_changed_at = models.DateTimeField(default=timezone.now,
                                             editable=False)

    class Meta:
        abstract = True

    def activate(self):
        if self.is_active: return

        self.is_active = True
        self.inactive_note = ''
        self.active_changed_at = timezone.now()
        self.save(update_fields=['is_active', 'inactive_note',
                                 'active_changed_at'])

        post_activate.send(sender=self.__class__, instance=self)

    def inactivate(self, note=None):
        if not self.is_active: return

        self.is_active = False
        self.inactive_note = note or ''
        self.active_changed_at = timezone.now()
        self.save(update_fields=['is_active', 'inactive_note',
                                 'active_changed_at'])

        post_inactivate.send(sender=self.__class__, instance=self)


class DirtyMixin(models.Model):
    """Adapted from https://github.com/smn/django-dirtyfields """

    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        super(DirtyMixin, self).__init__(*args, **kwargs)
        self._snapshot = self._as_dict()

    def _as_dict(self):
        return dict([(f.name, getattr(self, f.name))
                     for f in self._meta.fields if not f.rel])

    def get_dirty_fields(self):
        new_state = self._as_dict()
        return dict([(key, value)
                     for key, value in self._snapshot.iteritems()
                     if value != new_state[key]])

    def is_dirty(self):
        if not self.pk: return True
        return bool(self.get_dirty_fields())

    def save(self, *args, **kwargs):
        super(DirtyMixin, self).save(*args, **kwargs)
        self._snapshot = self._as_dict()


class AbstractModel(JSONMixin, UpdateMixin, models.Model):
    class Meta:
        abstract = True


class AbstractTimestampModel(TimestampMixin, AbstractModel):
    class Meta(TimestampMixin.Meta, AbstractModel.Meta):
        abstract = True


from cabbie.common.receivers import *
