import functools
import hashlib
import logging

import simplejson as json

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import signals
from django.db.models.manager import ensure_default_manager
from django.utils.encoding import smart_unicode


logger = logging.getLogger(__name__)


class SeparatedField(models.TextField):
    __metaclass__ = models.SubfieldBase

    def __init__(self, *args, **kwargs):
        self._separator = kwargs.pop('separator')
        super(SeparatedField, self).__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super(SeparatedField, self).deconstruct()
        kwargs['separator'] = self._separator
        return name, path, args, kwargs

    def to_python(self, value):
        if self.blank and value is None:
            return None
        if isinstance(value, list):
            return value
        return [e.strip() for e in value.split(self._separator) if e.strip()]

    def get_prep_value(self, value):
        return self._separator.join(value)

    def value_to_string(self, obj):
        return smart_unicode(self.get_prep_value(self._get_val_from_obj(obj)))

    def value_from_object(self, obj):
        return self.get_prep_value(self._get_val_from_obj(obj))


class TextDictField(models.TextField):
    __metaclass__ = models.SubfieldBase

    def to_python(self, value):
        if self.blank and value is None:
            return None
        if isinstance(value, dict):
            return value
        return dict([
            (token.strip() for token in line.split(u':'))
            for line in value.split(u'\n') if line.strip()])

    def get_prep_value(self, value):
        return u'\n'.join([u': '.join([k, v]) for k, v in value.iteritems()])

    def value_to_string(self, obj):
        return smart_unicode(self.get_prep_value(self._get_val_from_obj(obj)))

    def value_from_object(self, obj):
        return self.get_prep_value(self._get_val_from_obj(obj))


class JSONField(models.TextField):
    """A field that stores python structures as JSON strings on database.

    Adapted from django-social-auth
    (https://github.com/omab/django-social-auth/)
    """
    __metaclass__ = models.SubfieldBase

    def to_python(self, value):
        """
        Convert the input JSON value into python structures, raises
        django.core.exceptions.ValidationError if the data can't be converted.
        """
        if self.blank and value is None:
            return None
        if isinstance(value, basestring):
            try:
                return json.loads(value)
            except Exception, e:
                raise ValidationError(str(e))
        else:
            return value

    def validate(self, value, model_instance):
        """Check value is a valid JSON string, raise ValidationError on
        error."""
        if isinstance(value, basestring):
            super(JSONField, self).validate(value, model_instance)
            try:
                json.loads(value)
            except Exception, e:
                raise ValidationError(str(e))

    def get_prep_value(self, value):
        """Convert value to JSON string before save"""
        try:
            return json.dumps(value)
        except Exception, e:
            raise ValidationError(str(e))

    def value_to_string(self, obj):
        """Return value from object converted to string properly"""
        return smart_unicode(self.get_prep_value(self._get_val_from_obj(obj)))

    def value_from_object(self, obj):
        """Return value dumped to string."""
        return self.get_prep_value(self._get_val_from_obj(obj))


class HashFieldMixin(object):
    hash_field_name_format = '{field_name}_hash'
    hash_func = hashlib.sha1
    hash_length = 40

    def __init__(self, *args, **kwargs):
        self._hash_unique = kwargs.pop('unique', False)
        self._hash_field_name = None
        super(HashFieldMixin, self).__init__(*args, **kwargs)

    # Overriden
    # ---------

    def contribute_to_class(self, cls, name):
        super(HashFieldMixin, self).contribute_to_class(cls, name)

        self._hash_field_name = self._get_hash_field_name(name)

        signals.pre_init.connect(self._on_pre_init, sender=cls, weak=False)
        signals.class_prepared.connect(self._on_class_prepared, sender=cls)

    def pre_save(self, instance, add):
        value = super(HashFieldMixin, self).pre_save(instance, add)
        setattr(instance, self._hash_field_name, self._get_hash_value(value))
        return value

    # Prviate
    # -------

    def _on_pre_init(self, signal, sender, args, kwargs, **dummy):
        if self.name in kwargs:
            kwargs[self._hash_field_name] = \
                self._get_hash_value(kwargs[self.name])

    def _on_class_prepared(self, signal, sender, **kwargs):
        model = sender
        meta = model._meta

        if not meta.abstract:
            hash_field = models.CharField(max_length=self.hash_length,
                                          unique=self._hash_unique)
            hash_field.contribute_to_class(model, self._hash_field_name)

        ensure_default_manager(model)

        for _, name, manager in (meta.abstract_managers
                                 + meta.concrete_managers):
            setattr(manager, 'get_by_hash', functools.partial(
                self._get_by_hash, manager))
            setattr(manager, 'filter_by_hash', functools.partial(
                self._filter_by_hash, manager))
            setattr(manager, 'exists_by_hash', functools.partial(
                self._exists_by_hash, manager))

    def _get_hash_field_name(self, name):
        return self.hash_field_name_format.format(field_name=name)

    def _get_hash_value(self, value):
        return self.hash_func(value).hexdigest()

    # Manager proxy methods
    # ---------------------

    def _get_by_hash(self, manager, **kwargs):
        return manager.get(**dict([
            (self._get_hash_field_name(key), self._get_hash_value(value))
            for key, value in kwargs.iteritems()]))

    def _filter_by_hash(self, manager, **kwargs):
        return manager.filter(**dict([
            (self._get_hash_field_name(key), self._get_hash_value(value))
            for key, value in kwargs.iteritems()]))

    def _exists_by_hash(self, manager, **kwargs):
        return self._filter_by_hash(manager, **kwargs).exists()


class HashCharField(HashFieldMixin, models.CharField):
    pass


class HashURLField(HashFieldMixin, models.URLField):
    pass
