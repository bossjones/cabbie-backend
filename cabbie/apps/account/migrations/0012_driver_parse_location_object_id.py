# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0011_passenger_affiliation'),
    ]

    operations = [
        migrations.AddField(
            model_name='driver',
            name='parse_location_object_id',
            field=models.CharField(max_length=20, null=True, verbose_name='Parse \uc704\uce58\uc815\ubcf4 \uc624\ube0c\uc81d\ud2b8 ID', blank=True),
            preserve_default=True,
        ),
    ]
