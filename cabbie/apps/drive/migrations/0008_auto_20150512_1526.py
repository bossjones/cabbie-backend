# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('drive', '0007_auto_20150418_0045'),
    ]

    operations = [
        migrations.AlterField(
            model_name='request',
            name='approval',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, verbose_name='\uc2b9\uc778\ub41c \ubc30\ucc28', blank=True, to='drive.Ride', null=True),
        ),
        migrations.AlterField(
            model_name='ride',
            name='driver',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, verbose_name='\uae30\uc0ac', blank=True, to='account.Driver', null=True),
        ),
    ]
