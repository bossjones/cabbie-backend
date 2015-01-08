# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0002_auto_20150107_1616'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_email_agreed',
            field=models.BooleanField(default=False, verbose_name='\uc774\uba54\uc77c \uc218\uc2e0\ub3d9\uc758'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='user',
            name='is_sms_agreed',
            field=models.BooleanField(default=False, verbose_name='SMS \uc218\uc2e0\ub3d9\uc758'),
            preserve_default=True,
        ),
    ]
