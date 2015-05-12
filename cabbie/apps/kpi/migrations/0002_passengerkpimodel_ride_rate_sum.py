# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('kpi', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='passengerkpimodel',
            name='ride_rate_sum',
            field=models.PositiveIntegerField(default=0, verbose_name='\ud569\uc0b0\ud3c9\uc810'),
            preserve_default=False,
        ),
    ]
