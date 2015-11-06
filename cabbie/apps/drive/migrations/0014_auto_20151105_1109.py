# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('drive', '0013_requestnormalized_reason'),
    ]

    operations = [
        migrations.AlterField(
            model_name='requestnormalized',
            name='reason',
            field=models.CharField(default=b'', max_length=100, verbose_name='Reason'),
            preserve_default=True,
        ),
    ]
