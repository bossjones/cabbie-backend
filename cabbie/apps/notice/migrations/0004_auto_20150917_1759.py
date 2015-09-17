# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('notice', '0003_auto_20150728_1738'),
    ]

    operations = [
        migrations.AddField(
            model_name='notice',
            name='link',
            field=models.URLField(null=True, verbose_name='\uc0c1\uc138\ub9c1\ud06c', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='notice',
            name='notice_type',
            field=models.CharField(default=b'event', max_length=10, verbose_name='\ud0c0\uc785', choices=[(b'event', '\uc774\ubca4\ud2b8'), (b'update', '\uc5c5\ub370\uc774\ud2b8'), (b'news', '\ubc31\uae30\uc0ac \ub274\uc2a4')]),
            preserve_default=True,
        ),
    ]
