# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('affiliation', '0002_auto_20150506_1044'),
    ]

    operations = [
        migrations.AddField(
            model_name='affiliation',
            name='event_end_at',
            field=models.DateField(default=django.utils.timezone.now, verbose_name='\uc774\ubca4\ud2b8 \uc885\ub8cc\uc77c\uc790'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='affiliation',
            name='event_start_at',
            field=models.DateField(default=django.utils.timezone.now, verbose_name='\uc774\ubca4\ud2b8 \uc2dc\uc791\uc77c\uc790'),
            preserve_default=True,
        ),
    ]
