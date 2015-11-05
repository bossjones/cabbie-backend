# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('drive', '0012_requestnormalized'),
    ]

    operations = [
        migrations.AddField(
            model_name='requestnormalized',
            name='reason',
            field=models.CharField(default=b'', max_length=50, verbose_name='Reason'),
            preserve_default=True,
        ),
    ]
