# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('drive', '0005_request_contacts_by_distance'),
    ]

    operations = [
        migrations.AlterField(
            model_name='request',
            name='passenger',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, verbose_name='\uc2b9\uac1d', to='account.Passenger', null=True),
        ),
    ]
