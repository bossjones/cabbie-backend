# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('notice', '0004_auto_20150917_1759'),
    ]

    operations = [
        migrations.AddField(
            model_name='notice',
            name='visibility',
            field=models.CharField(default=b'visibility_all', max_length=30, verbose_name='\ud0c0\uac9f', choices=[(b'visibility_all', '\uc804\uccb4'), (b'visibility_driver', '\uae30\uc0ac'), (b'visibility_passenger', '\uc2b9\uac1d')]),
            preserve_default=True,
        ),
    ]
