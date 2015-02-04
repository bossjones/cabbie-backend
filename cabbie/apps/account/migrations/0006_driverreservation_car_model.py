# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0005_user_app_version'),
    ]

    operations = [
        migrations.AddField(
            model_name='driverreservation',
            name='car_model',
            field=models.CharField(default='', max_length=50, verbose_name='\ucc28\ub7c9\ubaa8\ub378', blank=True),
            preserve_default=True,
        ),
    ]
