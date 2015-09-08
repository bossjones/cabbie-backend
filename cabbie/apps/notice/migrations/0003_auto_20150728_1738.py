# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('notice', '0002_auto_20150528_1305'),
    ]

    operations = [
        migrations.AlterField(
            model_name='apppopup',
            name='link',
            field=models.URLField(null=True, verbose_name='\uc0c1\uc138\ub9c1\ud06c', blank=True),
        ),
    ]
