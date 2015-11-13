# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('event', '0005_auto_20151111_1200'),
    ]

    operations = [
        migrations.AddField(
            model_name='cueventpassengers',
            name='auth_date',
            field=models.CharField(max_length=20, null=True, verbose_name='\uc2b9\uc778\uc77c\uc790', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='cueventpassengers',
            name='auth_id',
            field=models.CharField(max_length=20, null=True, verbose_name='\uc2b9\uc778\ubc88\ud638', blank=True),
            preserve_default=True,
        ),
    ]
