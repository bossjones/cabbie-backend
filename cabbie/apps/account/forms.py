# -*- coding: utf-8 -*-

from django import forms
from django.utils.translation import ugettext_lazy as _

from cabbie.apps.education.models import Education

class EducationSelectForm(forms.Form):
    _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)
    education = forms.ModelChoiceField(Education.objects, label=_('교육'))
