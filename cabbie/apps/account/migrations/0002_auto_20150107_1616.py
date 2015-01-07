# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='ride_count',
        ),
        migrations.AlterField(
            model_name='driver',
            name='car_model',
            field=models.CharField(max_length=50, verbose_name='\ucc28\ub7c9\ubaa8\ub378', blank=True),
        ),
    ]
