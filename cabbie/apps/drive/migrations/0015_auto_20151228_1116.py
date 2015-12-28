# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('drive', '0014_auto_20151105_1109'),
    ]

    operations = [
        migrations.AlterField(
            model_name='region',
            name='depth',
            field=models.PositiveIntegerField(default=1, verbose_name='Depth'),
            preserve_default=True,
        ),
    ]
