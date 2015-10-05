# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import cabbie.common.fields
import cabbie.common.models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='RidePointEvent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='\uc0dd\uc131\uc2dc\uac04', editable=False, db_index=True)),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='\uac31\uc2e0\uc2dc\uac04', editable=False, db_index=True)),
                ('name', models.CharField(max_length=20, verbose_name='\uc774\ub984')),
                ('starts_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='\uc2dc\uc791\uc2dc\uac01')),
                ('ends_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='\uc885\ub8cc\uc2dc\uac01')),
                ('is_first_come_first_served_basis', models.BooleanField(default=False, verbose_name='\uc120\ucc29\uc21c \uc5ec\ubd80')),
                ('capacity', models.PositiveIntegerField(default=0, verbose_name='\ub300\uc0c1 \uac74\uc218 (\uc120\ucc29\uc21c\uc77c \ub54c\ub9cc \uc801\uc6a9)')),
                ('event_point', models.PositiveIntegerField(verbose_name='\uc9c0\uae09 \uc608\uc815 \ud3ec\uc778\ud2b8')),
                ('applied_count', models.PositiveIntegerField(default=0, verbose_name='\uc801\uc6a9\uc218')),
                ('is_accomplished', models.BooleanField(default=False, verbose_name='\ub2ec\uc131\uc5ec\ubd80')),
                ('priority', models.PositiveIntegerField(unique=True, verbose_name='\uc6b0\uc120\uc21c\uc704')),
                ('specification_type', models.CharField(default=b'none', max_length=20, verbose_name='\uc870\uac74', choices=[(b'none', '\uc5c6\uc74c'), (b'limited_per_day', '\uc77c\ub2f9 \ud69f\uc218\uc81c\ud55c'), (b'limited_per_person', '\uc778\ub2f9 \ud69f\uc218\uc81c\ud55c')])),
                ('specification_limit_count', models.PositiveIntegerField(default=0, verbose_name='\uc218')),
                ('applied_passengers', cabbie.common.fields.JSONField(default=b'{}', verbose_name='\uad00\ub828\ub41c \uc2b9\uac1d\ub4e4')),
            ],
            options={
                'ordering': ['-created_at'],
                'abstract': False,
                'verbose_name': '\ud0d1\uc2b9 \ud3ec\uc778\ud2b8 \uc774\ubca4\ud2b8',
                'verbose_name_plural': '\ud0d1\uc2b9 \ud3ec\uc778\ud2b8 \uc774\ubca4\ud2b8',
            },
            bases=(cabbie.common.models.JSONMixin, cabbie.common.models.UpdateMixin, models.Model),
        ),
    ]
