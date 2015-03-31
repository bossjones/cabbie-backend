# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import cabbie.common.fields
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('drive', '0003_auto_20150329_2234'),
    ]

    operations = [
        migrations.AddField(
            model_name='request',
            name='destination',
            field=cabbie.common.fields.JSONField(default=b'{}', verbose_name='\ub3c4\ucc29\uc9c0'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='request',
            name='destination_location',
            field=django.contrib.gis.db.models.fields.PointField(srid=4326, null=True, verbose_name='\ub3c4\ucc29\uc9c0 \uc88c\ud45c', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='request',
            name='distance',
            field=models.PositiveIntegerField(default=0, verbose_name='\uc694\uccad\uac70\ub9ac'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='request',
            name='source',
            field=cabbie.common.fields.JSONField(default=b'{}', verbose_name='\ucd9c\ubc1c\uc9c0'),
            preserve_default=True,
        ),
    ]
