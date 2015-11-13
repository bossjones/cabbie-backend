# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('event', '0008_auto_20151113_1441'),
    ]

    operations = [
        migrations.AddField(
            model_name='cueventpassengers',
            name='res_msg',
            field=models.CharField(max_length=100, null=True, verbose_name='\uc751\ub2f5\uba54\uc2dc\uc9c0', blank=True),
            preserve_default=True,
        ),
    ]
