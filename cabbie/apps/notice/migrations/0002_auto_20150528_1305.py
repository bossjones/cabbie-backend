# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import tinymce.models


class Migration(migrations.Migration):

    dependencies = [
        ('notice', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='apppopup',
            name='content',
            field=tinymce.models.HTMLField(verbose_name='\ub0b4\uc6a9', blank=True),
        ),
        migrations.AlterField(
            model_name='notice',
            name='content',
            field=tinymce.models.HTMLField(verbose_name='\ub0b4\uc6a9', blank=True),
        ),
    ]
