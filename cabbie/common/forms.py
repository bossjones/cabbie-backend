# encoding: utf8

from django import forms
from django.contrib.admin.forms import (
    AdminAuthenticationForm as BaseAdminAuthenticationForm)
from django.contrib.auth import authenticate


class AdminAuthenticationForm(BaseAdminAuthenticationForm):
    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            self.user_cache = authenticate(username=username,
                                           password=password)
            if self.user_cache is None:
                return self.add_error('password',
                                      u'비밀번호가 일치하지 않습니다.')
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data
