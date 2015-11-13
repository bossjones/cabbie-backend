# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('event', '0006_auto_20151112_1639'),
    ]

    operations = [
        migrations.AddField(
            model_name='cueventpassengers',
            name='is_issue_canceled',
            field=models.BooleanField(default=False, verbose_name='\ubc1c\ud589\ucde8\uc18c\uc5ec\ubd80'),
            preserve_default=True,
        ),
    ]
