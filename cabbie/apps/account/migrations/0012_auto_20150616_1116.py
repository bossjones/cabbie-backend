# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0011_passenger_affiliation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='passenger',
            name='affiliation',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, verbose_name='\uc81c\ud734\uc0ac', blank=True, to='affiliation.Affiliation', null=True),
        ),
    ]
