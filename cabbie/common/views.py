from coffin.views.generic import (
    View as BaseView,
    TemplateView as BaseTemplateView,
    RedirectView as BaseRedirectView,
    DetailView as BaseDetailView,
    ListView as BaseListView,
    FormView as BaseFormView,
    CreateView as BaseCreateView,
    UpdateView as BaseUpdateView,
    DeleteView as BaseDeleteView,
)
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.utils.decorators import method_decorator


# Mixins
# ------

class Atomic(object):
    @method_decorator(transaction.atomic)
    def post(self, request, *args, **kwargs):
        return super(Atomic, self).post(request, *args, **kwargs)


class LoginRequired(object):
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(LoginRequired, self).dispatch(*args, **kwargs)


# View
# ----

class View(BaseView)                     : pass
class TemplateView(BaseTemplateView)     : pass
class RedirectView(BaseRedirectView)     : pass
class DetailView(BaseDetailView)         : pass
class ListView(BaseListView)             : pass
class FormView(Atomic, BaseFormView)     : pass
class CreateView(Atomic, BaseCreateView) : pass
class UpdateView(Atomic, BaseUpdateView) : pass
class DeleteView(Atomic, BaseDeleteView) : pass
