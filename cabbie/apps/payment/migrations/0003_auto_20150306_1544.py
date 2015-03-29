# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0002_auto_20150109_0501'),
    ]

    operations = [
        migrations.AddField(
            model_name='driverreturn',
            name='note',
            field=models.CharField(default='', max_length=1000, verbose_name='\uba54\ubaa8', blank=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='passengerreturn',
            name='note',
            field=models.CharField(default='', max_length=1000, verbose_name='\uba54\ubaa8', blank=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='transaction',
            name='state',
            field=models.CharField(default=b'planned', max_length=30, verbose_name='\uc0c1\ud0dc', choices=[(b'planned', '\uc608\uc815'), (b'done', '\uc644\ub8cc')]),
            preserve_default=True,
        ),
    ]
