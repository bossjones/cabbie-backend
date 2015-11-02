# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('kpi', '0006_auto_20150821_1456'),
    ]

    operations = [
        migrations.AddField(
            model_name='passengerkpimodel',
            name='ride_long',
            field=models.PositiveIntegerField(default=0, verbose_name='6-10km'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='passengerkpimodel',
            name='ride_medium',
            field=models.PositiveIntegerField(default=0, verbose_name='3-6km'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='passengerkpimodel',
            name='ride_short',
            field=models.PositiveIntegerField(default=0, verbose_name='0-3km'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='passengerkpimodel',
            name='ride_xlong',
            field=models.PositiveIntegerField(default=0, verbose_name='10km-'),
            preserve_default=True,
        ),
    ]
