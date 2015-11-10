# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('event', '0004_auto_20151110_1154'),
    ]

    operations = [
        migrations.AddField(
            model_name='cueventpassengers',
            name='api_response_code',
            field=models.CharField(max_length=2, null=True, verbose_name='API\uc751\ub2f5\ucf54\ub4dc', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='cueventpassengers',
            name='pin_no',
            field=models.CharField(max_length=30, null=True, verbose_name='\ubc14\ucf54\ub4dc\ubc88\ud638', blank=True),
            preserve_default=True,
        ),
    ]
