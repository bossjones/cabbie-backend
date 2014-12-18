# encoding: utf8

import cStringIO
import os
from urlparse import urlparse

import random
from datetime import datetime, timedelta

from django.core.files import File
from django.core.files.storage import default_storage
from django.db import models
from django.db.models import Max
from django.db.models.fields.related import RelatedField
from django.template.defaultfilters import slugify
from django.utils import timezone
from PIL import Image
import requests

from cabbie.common.signals import (post_activate, post_inactivate,
                                   post_status_change)
from cabbie.utils.ds import pick
from cabbie.utils.image import reset, resize, thumbnail
from cabbie.utils.increment import Incrementer
from cabbie.utils.rand import random_hash


Buffer = cStringIO.StringIO


# Mixins
# ------

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
    created_at = models.DateTimeField(u'생성시간', default=timezone.now,
                                      db_index=True, editable=False)
    updated_at = models.DateTimeField(u'갱신시간', default=timezone.now,
                                      db_index=True, editable=False)

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


class ImageMixin(DirtyMixin):
    # TODO: Delete image files when the image objects are deleted

    IMAGE_TYPES = ()
    """Specifies the sizes and shapes of the images to be used.

    The 's' suffix means the image is cropped to a square shape using
    specified size as width and height.

    The 'original' type is reserved for the original uploaded image.

    e.g. IMAGE_TYPES = ('500', '200s', '100s')
    """

    class Meta:
        abstract = True

    @property
    def url(self):
        return self.get_image_url('original')

    def _refresh_image_key(self):
        # TODO: Check existence in storage before allocating
        self.image_key = random_hash()

    def _get_image_key(self):
        if not self.image_key:
            self._refresh_image_key()
        return self.image_key

    def _get_prefix(self):
        DEPTH = 3
        UNIT_SIZE = 2

        key = self._get_image_key()
        prefix = ''
        for i in range(DEPTH):
            prefix += key[i*UNIT_SIZE:(i + 1)*UNIT_SIZE] + '/'
        return prefix

    def get_upload_path(self, image_type, filename=None):
        # Whenever a new file is uploaded, refresh the image key so that
        # new path is used to avoid image caching
        if filename:
            self._refresh_image_key()

        return 'image/{image_type}/{prefix}{key}.{ext}'.format(
            image_type=image_type,
            prefix=self._get_prefix(),
            key=self._get_image_key(),
            ext=filename.split('.')[-1] if filename else 'jpg',
        )

    def get_image_url(self, image_type):
        return (self.image.url if image_type == 'original' else
                default_storage.url(self.get_upload_path(image_type)))

    def get_image_urls(self):
        return dict([(image_type, self.get_image_url(image_type))
                     for image_type in list(self.IMAGE_TYPES) + ['original']])

    def get_image_size(self, image_type):
        if not self.image_width or not self.image_height:
            return (0, 0)
        if image_type == 'original':
            return (self.image_width, self.image_height)
        is_square = image_type[-1].lower() == 's'
        width = int(image_type[:-1] if is_square else image_type)
        height = (width if is_square else
                  int(round(self.image_height * width / self.image_width)))
        return (width, height)

    def create_images(self, image_types=None):
        if image_types is None:
            image_types = self.IMAGE_TYPES

        if not image_types:
            return
        if not self.image:
            return

        # Load the original image
        if self.image.closed:
            self.image.open()
        self.image.seek(0)
        image = reset(Image.open(self.image))

        for image_type in image_types:
            image_type = unicode(image_type)
            is_square = image_type[-1].lower() == 's'
            width, height = self.get_image_size(image_type)

            if is_square:
                new_image = thumbnail(
                    image, size=[width, height], crop='middle')
            else:
                new_image = resize(image, [width, height])

            data = Buffer()
            new_image.save(data, 'jpeg', quality=100)
            default_storage.save(self.get_upload_path(image_type), File(data))

    def load_from_url(self, image_url, save=True):
        filename = os.path.basename(urlparse(image_url).path)
        data = Buffer(requests.get(image_url).content)
        self.image.save(filename, File(data), save=save)

    def save(self, *args, **kwargs):
        is_dirty_image = not bool(self.pk) \
                         or 'image' in self.get_dirty_fields() \
                         or 'image_key' in self.get_dirty_fields()

        super(ImageMixin, self).save(*args, **kwargs)

        # Create images only when the image fields is modified
        # or newly created
        if is_dirty_image:
            self.create_images()


def _upload_to(instance, filename):
    return instance.get_upload_path('original', filename)


class NullableImageMixin(ImageMixin):
    image = models.ImageField(upload_to=_upload_to, blank=True, null=True,
                              width_field='image_width',
                              height_field='image_height')
    image_key = models.CharField(max_length=100, blank=True)
    image_width = models.IntegerField(blank=True, null=True)
    image_height = models.IntegerField(blank=True, null=True)

    class Meta:
        abstract = True

    def get_image_url(self, image_type):
        return (super(NullableImageMixin, self).get_image_url(image_type)
                if self.image else self.get_default_image_url(image_type))

    def get_default_image_url(self, image_type):
        raise NotImplementedError


class StrictImageMixin(ImageMixin):
    image = models.ImageField(upload_to=_upload_to,
                              width_field='image_width',
                              height_field='image_height')
    image_key = models.CharField(max_length=40)
    image_width = models.IntegerField()
    image_height = models.IntegerField()

    class Meta:
        abstract = True


# Abstract
# --------

class AbstractModel(JSONMixin, UpdateMixin, models.Model):
    class Meta:
        abstract = True


class AbstractPositionImage(StrictImageMixin, AbstractModel):
    position = models.PositiveIntegerField()

    class Meta(StrictImageMixin.Meta, AbstractModel.Meta):
        abstract = True
        ordering = ['position']

    @property
    def order(self):
        return self.position

    def get_default_position(self):
        return (self.owner.images.all().aggregate(
            max=Max('position'))['max'] or 0) + 1

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if not self.position:
            self.position = self.get_default_position()
            if update_fields is not None:
                update_fields.append('position')
        super(AbstractPositionImage, self).save(
            force_insert, force_update, using, update_fields)


class AbstractTimestampModel(TimestampMixin, AbstractModel):
    class Meta(TimestampMixin.Meta, AbstractModel.Meta):
        abstract = True


from cabbie.common.receivers import *
