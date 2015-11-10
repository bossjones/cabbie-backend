# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('event', '0003_cueventpassengers'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cueventpassengers',
            name='passenger',
            field=models.OneToOneField(related_name='cu_event', null=True, blank=True, to='account.Passenger'),
            preserve_default=True,
        ),
    ]
