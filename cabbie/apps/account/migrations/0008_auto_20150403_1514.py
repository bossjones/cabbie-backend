# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0007_driver_is_educated'),
    ]

    operations = [
        migrations.AddField(
            model_name='driver',
            name='province',
            field=models.CharField(default=b'', max_length=10, verbose_name='\uc2dc\ub3c4'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='driver',
            name='region',
            field=models.CharField(default=b'', max_length=20, verbose_name='\uc9c0\uc5ed'),
            preserve_default=True,
        ),
    ]
