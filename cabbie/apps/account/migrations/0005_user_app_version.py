# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0004_user_push_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='app_version',
            field=models.CharField(default=b'', max_length=10, verbose_name='\uc571\ubc84\uc804'),
            preserve_default=True,
        ),
    ]
