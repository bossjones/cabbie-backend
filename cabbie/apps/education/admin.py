# encoding: utf8

from django.contrib import admin

from cabbie.common.admin import AbstractAdmin
from cabbie.apps.education.models import Education

class EducationAdmin(AbstractAdmin): 
    addable = True
    list_display = (
        'id', 'name', 'place', 'started_at', 'lecturer',
    )

    search_fields = (
        '=id',
        'name',
        'place',
        'lecturer',
    )
    ordering = ('-started_at',)

admin.site.register(Education, EducationAdmin)
