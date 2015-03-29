# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('drive', '0002_auto_20150328_2236'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ride',
            name='passenger',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, verbose_name='\uc2b9\uac1d', to='account.Passenger', null=True),
        ),
    ]
