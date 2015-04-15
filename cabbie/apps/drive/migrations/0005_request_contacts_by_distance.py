# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import cabbie.common.fields


class Migration(migrations.Migration):

    dependencies = [
        ('drive', '0004_auto_20150331_1616'),
    ]

    operations = [
        migrations.AddField(
            model_name='request',
            name='contacts_by_distance',
            field=cabbie.common.fields.JSONField(default=b'{}', verbose_name='\uac70\ub9ac\ubcc4 \ubcf4\ub0b8\uae30\uc0ac \ub9ac\uc2a4\ud2b8'),
            preserve_default=True,
        ),
    ]
