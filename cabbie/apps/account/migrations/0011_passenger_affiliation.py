# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0010_auto_20150512_2205'),
        ('affiliation', '__first__'),
    ]

    operations = [
        migrations.AddField(
            model_name='passenger',
            name='affiliation',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, verbose_name='\uc81c\ud734\uc0ac', to='affiliation.Affiliation', null=True),
            preserve_default=True,
        ),
    ]
