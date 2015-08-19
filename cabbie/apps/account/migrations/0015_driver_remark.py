# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0014_auto_20150819_1348'),
    ]

    operations = [
        migrations.AddField(
            model_name='driver',
            name='remark',
            field=models.CharField(default=b'', max_length=100, verbose_name='\ube44\uace0', blank=True),
            preserve_default=True,
        ),
    ]
