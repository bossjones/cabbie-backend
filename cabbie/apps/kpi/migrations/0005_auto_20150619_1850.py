# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('kpi', '0004_auto_20150619_1728'),
    ]

    operations = [
        migrations.AlterField(
            model_name='passengerkpimodel',
            name='subscriber',
            field=models.PositiveIntegerField(null=True, verbose_name='\uc2e0\uaddc\uac00\uc785\uc790'),
        ),
    ]
