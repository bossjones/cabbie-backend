# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0003_auto_20150109_0252'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='push_id',
            field=models.CharField(default=b'', max_length=30, verbose_name='\ud478\uc2dc\uc544\uc774\ub514'),
            preserve_default=True,
        ),
    ]
