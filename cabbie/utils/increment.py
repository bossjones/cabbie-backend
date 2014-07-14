from django.db.models import F, get_model


class IncrementInfo(object):
    def __init__(self, model, pk_value):
        self._model = model
        self._pk_value = pk_value
        self._field_map = {}

    @property
    def model(self):
        return self._model

    @property
    def pk_value(self):
        return self._pk_value

    def add_field(self, field, offset):
        if field in self._field_map:
            self._field_map[field] += offset
        else:
            self._field_map[field] = offset

    def iter_field_values(self):
        return self._field_map.iteritems()


class Incrementer(object):
    """Increments a model's field value by a specified amount.

    Usage example:
      inc = Incrementer()
      inc \
        .add(Craver, craver.id, 'foo_count', 1 ) \
        .add(Craver, craver.id, 'boo_count', 2 ) \
        .add(Store, store.id, 'foo_count', 1 ) \
        .run()
    """
    def __init__(self, reverse=False, pk_field_name='id'):
        self._reverse = reverse
        self._target_values = []
        self._pk_field_name = pk_field_name
        super(Incrementer, self).__init__()

    def add(self, model, pk_value, field_name, offset=1):
        """Adds incrementable model and field names. """
        if pk_value is not None:
            if isinstance(model, basestring):
                app_name, model_name = model.split('.')
                model = get_model(app_name, model_name)

            self._target_values.append(dict(
                model=model,
                pk_value=pk_value,
                field_name=field_name,
                offset=offset if not self._reverse else -1 * offset
            ))
        return self

    def run(self, *args, **kwargs):
        """Make sure that base incrementer doesn't incur any exceptions.

        Since this function is most likely be used within signal, we shouldn't
        block this!
        """
        info_list = self._merge()
        self._run(info_list)

    def _merge(self):
        class_dict = {}

        for value in self._target_values:
            key = (value['model'], value['pk_value'])
            class_dict \
                .setdefault(key, IncrementInfo(*key)) \
                .add_field(value['field_name'], value['offset'])

        return class_dict.values()

    def _run(self, info_list):
        for info in info_list:
            update_kwargs = {}

            for field_name, offset in info.iter_field_values():
                update_kwargs[field_name] = F(field_name) + offset

            info.model._default_manager \
                .filter(**{ self._pk_field_name: info.pk_value }) \
                .update(**update_kwargs)


