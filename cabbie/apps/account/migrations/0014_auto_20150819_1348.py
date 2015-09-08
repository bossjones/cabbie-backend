# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0013_user_device_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='driver',
            name='company',
            field=models.CharField(default='\uac1c\uc778', max_length=50, verbose_name='\ud68c\uc0ac'),
        ),
        migrations.AlterField(
            model_name='driver',
            name='taxi_type',
            field=models.CharField(default=b'private', max_length=10, verbose_name='\ud0dd\uc2dc\uc885\ub958', choices=[(b'private', '\uac1c\uc778'), (b'luxury', '\ubaa8\ubc94')]),
        ),
    ]
