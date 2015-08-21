# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('notification', '0004_auto_20150821_1541'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='is_freezed',
            field=models.BooleanField(default=False, verbose_name='\uc0ac\uc6a9\uc81c\ud55c'),
            preserve_default=True,
        ),
    ]
