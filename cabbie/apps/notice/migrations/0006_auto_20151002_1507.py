# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc
import cabbie.common.models


class Migration(migrations.Migration):

    dependencies = [
        ('notice', '0005_notice_visibility'),
    ]

    operations = [
        migrations.AddField(
            model_name='notice',
            name='image',
            field=models.ImageField(height_field=b'image_height', width_field=b'image_width', null=True, upload_to=cabbie.common.models._upload_to, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='notice',
            name='image_height',
            field=models.IntegerField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='notice',
            name='image_key',
            field=models.CharField(max_length=100, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='notice',
            name='image_width',
            field=models.IntegerField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='notice',
            name='link_label',
            field=models.CharField(default='\uc790\uc138\ud788 \ubcf4\uae30', max_length=15, null=True, verbose_name='\uc0c1\uc138\ub9c1\ud06c \ubc84\ud2bc\uba85', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='notice',
            name='new_until',
            field=models.DateTimeField(default=datetime.datetime(2015, 10, 2, 6, 7, 18, 774800, tzinfo=utc), verbose_name='NEW \ud45c\uc2dc \ub9c8\uac10\uc2dc\uac04'),
            preserve_default=False,
        ),
    ]
