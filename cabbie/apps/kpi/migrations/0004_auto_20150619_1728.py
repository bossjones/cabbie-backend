# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('kpi', '0003_driverkpimodel'),
    ]

    operations = [
        migrations.AddField(
            model_name='passengerkpimodel',
            name='province',
            field=models.CharField(default=b'', max_length=10, null=True, verbose_name='\uc2dc\ub3c4', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='passengerkpimodel',
            name='region',
            field=models.CharField(default=b'', max_length=20, null=True, verbose_name='\uc9c0\uc5ed', blank=True),
            preserve_default=True,
        ),
    ]
