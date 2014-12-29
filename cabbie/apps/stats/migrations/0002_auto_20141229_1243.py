# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import cabbie.common.fields


class Migration(migrations.Migration):

    dependencies = [
        ('stats', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='driverridestatday',
            name='rides',
            field=cabbie.common.fields.JSONField(default=b'[]', verbose_name='\ud0d1\uc2b9\uac74'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='driverridestatmonth',
            name='rides',
            field=cabbie.common.fields.JSONField(default=b'[]', verbose_name='\ud0d1\uc2b9\uac74'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='driverridestatweek',
            name='rides',
            field=cabbie.common.fields.JSONField(default=b'[]', verbose_name='\ud0d1\uc2b9\uac74'),
            preserve_default=True,
        ),
        migrations.RemoveField(
            model_name='driverridestatday',
            name='count',
        ),
        migrations.RemoveField(
            model_name='driverridestatmonth',
            name='count',
        ),
        migrations.RemoveField(
            model_name='driverridestatweek',
            name='count',
        ),
    ]
