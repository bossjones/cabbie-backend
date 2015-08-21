# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('kpi', '0005_auto_20150619_1850'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='passengerkpimodel',
            options={'ordering': (b'id',), 'verbose_name': '\uc2b9\uac1d KPI', 'verbose_name_plural': '\uc2b9\uac1d KPI'},
        ),
    ]
