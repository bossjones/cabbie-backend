# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('event', '0007_cueventpassengers_is_issue_canceled'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cueventpassengers',
            name='passenger',
            field=models.OneToOneField(related_name='cu_event', null=True, on_delete=django.db.models.deletion.SET_NULL, blank=True, to='account.Passenger'),
            preserve_default=True,
        ),
    ]
