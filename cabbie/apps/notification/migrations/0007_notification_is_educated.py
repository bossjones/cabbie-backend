# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('notification', '0006_auto_20150821_1557'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='is_educated',
            field=models.NullBooleanField(verbose_name='\uad50\uc721\uc774\uc218\uc5ec\ubd80'),
            preserve_default=True,
        ),
    ]
