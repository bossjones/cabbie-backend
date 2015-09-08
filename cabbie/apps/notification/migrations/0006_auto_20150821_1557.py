# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('notification', '0005_auto_20150821_1554'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='is_freezed',
            field=models.BooleanField(default=False, verbose_name='\uc0ac\uc6a9\uc81c\ud55c\uc790 \ub300\uc0c1'),
            preserve_default=True,
        ),
    ]
