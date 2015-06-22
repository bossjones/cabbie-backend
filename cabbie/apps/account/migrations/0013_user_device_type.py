# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0012_auto_20150616_1116'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='device_type',
            field=models.CharField(default=b'', max_length=1, verbose_name='\uae30\uae30\uc885\ub958'),
            preserve_default=True,
        ),
    ]
