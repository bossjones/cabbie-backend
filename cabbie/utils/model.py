from django.db.models import get_model, Model
from django.utils.functional import SimpleLazyObject


def get_model_lazily(model):
    return SimpleLazyObject(lambda: get_model(model))

def has_child_model(model):
    if isinstance(model, Model) and hasattr(model, '__class__'):
        model = model.__class__
    return any([model in related.model._meta.get_parent_list()
                for related in model._meta.get_all_related_objects()])
