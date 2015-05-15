# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0009_auto_20150512_1703'),
    ]

    operations = [
        migrations.AlterField(
            model_name='driver',
            name='education',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, verbose_name='\uad50\uc721', blank=True, to='education.Education', null=True),
        ),
    ]
