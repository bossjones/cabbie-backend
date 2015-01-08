# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('drive', '0002_auto_20150103_1925'),
    ]

    operations = [
        migrations.AddField(
            model_name='location',
            name='driver_id',
            field=models.PositiveIntegerField(default=0, serialize=False, verbose_name='\uae30\uc0ac\uc544\uc774\ub514', primary_key=True),
            preserve_default=True,
        ),
        migrations.RemoveField(
            model_name='location',
            name='driver',
        ),
        migrations.RemoveField(
            model_name='location',
            name='id',
        ),
    ]
