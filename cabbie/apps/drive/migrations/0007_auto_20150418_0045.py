# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import cabbie.common.fields


class Migration(migrations.Migration):

    dependencies = [
        ('drive', '0006_auto_20150415_1043'),
    ]

    operations = [
        migrations.AddField(
            model_name='request',
            name='approval_driver_json',
            field=cabbie.common.fields.JSONField(null=True, verbose_name='\uc2b9\uc778\uae30\uc0ac \ub370\uc774\ud130', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='request',
            name='contacts',
            field=cabbie.common.fields.JSONField(default=b'[]', verbose_name='\ubcf4\ub0b8\uae30\uc0ac'),
        ),
        migrations.AlterField(
            model_name='request',
            name='contacts_by_distance',
            field=cabbie.common.fields.JSONField(default=b'{}', verbose_name='\uac70\ub9ac\ubcc4 \ubcf4\ub0b8\uae30\uc0ac'),
        ),
        migrations.AlterField(
            model_name='request',
            name='rejects',
            field=cabbie.common.fields.JSONField(default=b'[]', verbose_name='\uac70\uc808\uae30\uc0ac'),
        ),
    ]
