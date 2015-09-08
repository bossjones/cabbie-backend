# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('notification', '0002_auto_20150821_1459'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='is_test',
            field=models.BooleanField(default=False, verbose_name='\ud14c\uc2a4\ud2b8'),
            preserve_default=True,
        ),
    ]
