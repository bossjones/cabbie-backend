# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0004_auto_20150512_1528'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='recommend',
            field=models.ForeignKey(verbose_name='\ucd94\ucc9c', blank=True, to='recommend.Recommend', null=True),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='ride',
            field=models.ForeignKey(verbose_name='\ucf5c', blank=True, to='drive.Ride', null=True),
        ),
    ]
