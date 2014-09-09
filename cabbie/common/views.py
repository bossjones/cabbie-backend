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
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView as BaseGenericAPIView
from rest_framework.views import APIView as BaseAPIView

from cabbie.utils import json


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


class CsrfExcempt(object):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(CsrfExcempt, self).dispatch(*args, **kwargs)


class SecretRequired(object):
    def dispatch(self, request, *args, **kwargs):
        if request.META.get('HTTP_SECRET') != settings.SECRET_KEY:
            raise PermissionDenied('Secret required')
        return super(SecretRequired, self).dispatch(request, *args, **kwargs)


class HelperMixin(object):
    @classmethod
    def render_json_raw(cls, data, **response_kwargs):
        return HttpResponse(json.dumps(data), content_type='application/json',
                            **response_kwargs)
    @classmethod
    def render_json(cls, data=None, status=True, **response_kwargs):
        response = {
            'status': 'success' if status else 'failure',
            'data': data if data else {},
        }
        return cls.render_json_raw(response)

    @classmethod
    def render_error_msg(cls, msg, **response_kwargs):
        return cls.render_json({'msg': msg}, False)

    @classmethod
    def render_html(cls, data, **response_kwargs):
        return HttpResponse(data, content_type='text/html',
                            **response_kwargs)

    @classmethod
    def redirect(cls, url):
        return HttpResponseRedirect(url)


class APIMixin(object):
    @classmethod
    def render(cls, data=None, **response_kwargs):
        return Response(data or {}, **response_kwargs)

    @classmethod
    def render_error(cls, msg, code=None, status=status.HTTP_400_BAD_REQUEST):
        return cls.render({'error': {'code': code, 'msg': msg}}, status=status)


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


class APIView(APIMixin, BaseAPIView):
    pass


class GenericAPIView(APIMixin, BaseGenericAPIView):
    pass


class InternalView(CsrfExcempt, SecretRequired, Atomic, HelperMixin, View):
    pass
