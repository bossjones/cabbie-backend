# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0006_driverreservation_car_model'),
    ]

    operations = [
        migrations.AddField(
            model_name='driver',
            name='is_educated',
            field=models.BooleanField(default=False, verbose_name='\uad50\uc721\uc774\uc218\uc5ec\ubd80'),
            preserve_default=True,
        ),
    ]
